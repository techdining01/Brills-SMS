import requests
import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from .models import BankAccount, PaymentTransaction, PaymentBatch, PayrollRecord, AuditLog
from uuid import uuid4

class PaystackService:
    """Service for handling Paystack transfers and webhooks."""
    
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    def create_transfer_recipient(self, bank_account):
        """
        Create a transfer recipient on Paystack.
        Returns recipient_code or None if failed.
        """
        url = f"{self.BASE_URL}/transferrecipient"
        data = {
            "type": "nuban",
            "name": bank_account.account_name,
            "account_number": bank_account.account_number,
            "bank_code": bank_account.bank_code,
            "currency": "NGN"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            result = response.json()
            
            if result.get('status') and result.get('data'):
                return result['data'].get('recipient_code')
            else:
                return None
        except Exception as e:
            print(f"Error creating recipient: {e}")
            return None
    
    def initiate_transfer(self, recipient_code, amount, reference, reason="Salary Payment"):
        """
        Initiate a single transfer via Paystack.
        Returns (success: bool, transfer_code: str, message: str)
        """
        url = f"{self.BASE_URL}/transfer"
        
        # Convert to kobo
        amount_kobo = int(amount * 100)
        
        data = {
            "source": "balance",
            "amount": amount_kobo,
            "recipient": recipient_code,
            "reason": reason,
            "reference": reference
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            result = response.json()
            
            if result.get('status'):
                transfer_data = result.get('data', {})
                return (True, transfer_data.get('transfer_code'), result.get('message', 'Success'))
            else:
                return (False, None, result.get('message', 'Unknown error'))
        except requests.exceptions.RequestException as e:
            return (False, None, f"Network error: {str(e)}")
        except Exception as e:
            return (False, None, f"Error: {str(e)}")
    
    def verify_transfer(self, transfer_code):
        """
        Verify transfer status from Paystack.
        Returns (status: str, message: str)
        """
        url = f"{self.BASE_URL}/transfer/{transfer_code}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            result = response.json()
            
            if result.get('status') and result.get('data'):
                data = result['data']
                return (data.get('status'), data.get('reason', ''))
            else:
                return ('failed', result.get('message', 'Unknown error'))
        except Exception as e:
            return ('failed', str(e))
    
    @staticmethod
    def verify_webhook_signature(request):
        """
        Verify that webhook came from Paystack.
        """
        paystack_signature = request.headers.get('X-Paystack-Signature')
        if not paystack_signature:
            return False
        
        body = request.body
        computed_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            body,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, paystack_signature)


def process_payroll_payments(payroll_period, user):
    """
    Process all payments for a payroll period atomically.
    Creates batch and initiates transfers via Paystack.
    
    Returns: (batch, success_count, failed_records)
    """
    paystack = PaystackService()
    
    # Get all records that need payment
    records = payroll_period.records.filter(
        payee__bank_accounts__is_primary=True,
        payee__bank_accounts__is_approved=True
    ).distinct()
    
    if not records.exists():
        raise ValueError("No payroll records with approved bank accounts found.")
    
    # Create payment batch
    batch = PaymentBatch.objects.create(
        payroll_period=payroll_period,
        reference=f"BATCH-{uuid4().hex[:8].upper()}",
        total_amount=sum(r.net_pay for r in records),
        created_by=user
    )
    
    success_count = 0
    failed_records = []
    
    for record in records:
        # Get primary approved bank
        bank = record.payee.bank_accounts.filter(is_primary=True, is_approved=True).first()
        
        # Check if already paid or pending
        if record.transactions.filter(status__in=['success', 'pending']).exists():
            continue
        
        # Create transaction record immediately so it's no longer "Idle"
        reference = f"PAY-{record.id}-{uuid4().hex[:6].upper()}"
        payment_tx = PaymentTransaction.objects.create(
            payroll_record=record,
            batch=batch,
            amount=record.net_pay,
            currency="NGN",
            paystack_reference=reference,
            status='pending'
        )

        if not bank:
            payment_tx.status = 'failed'
            payment_tx.failure_reason = 'No approved primary bank account'
            payment_tx.save()
            failed_records.append({'record': record, 'reason': payment_tx.failure_reason})
            continue
        
        # Ensure recipient code exists
        if not bank.recipient_code:
            recipient_code = paystack.create_transfer_recipient(bank)
            if recipient_code:
                with transaction.atomic():
                    bank.recipient_code = recipient_code
                    bank.save()
            else:
                payment_tx.status = 'failed'
                payment_tx.failure_reason = 'Failed to create Paystack recipient'
                payment_tx.save()
                failed_records.append({'record': record, 'reason': payment_tx.failure_reason})
                continue
        
        # Initiate transfer (Network call outside transaction)
        success, transfer_code, message = paystack.initiate_transfer(
            recipient_code=bank.recipient_code,
            amount=record.net_pay,
            reference=reference,
            reason=f"Salary - {payroll_period}"
        )
        
        with transaction.atomic():
            payment_tx.refresh_from_db()
            if success:
                payment_tx.transfer_code = transfer_code
                payment_tx.status = 'success'
                payment_tx.response_data = {'message': message, 'transfer_code': transfer_code}
                payment_tx.save()
                success_count += 1
                
                # Audit log
                AuditLog.objects.create(
                    user=user,
                    action='PAY',
                    model_name='PayrollRecord',
                    object_id=str(record.id),
                    description=f"Initiated transfer to {record.payee} - {record.net_pay}"
                )
            else:
                payment_tx.status = 'failed'
                payment_tx.failure_reason = message
                payment_tx.response_data = {'error': message}
                payment_tx.save()
                
                failed_records.append({
                    'record': record,
                    'reason': message
                })
                
                # Audit log
                AuditLog.objects.create(
                    user=user,
                    action='FAIL',
                    model_name='PayrollRecord',
                    object_id=str(record.id),
                    description=f"Transfer failed: {message}"
                )
    
    batch.is_processed = True
    batch.save()
    
    return batch, success_count, failed_records


def retry_failed_payment(transaction_id, user):
    """
    Retry a failed payment transaction.
    Returns (success: bool, message: str)
    """
    paystack = PaystackService()
    
    try:
        payment_tx = PaymentTransaction.objects.get(id=transaction_id, status='failed')
    except PaymentTransaction.DoesNotExist:
        return (False, "Transaction not found or not in failed state")
    
    record = payment_tx.payroll_record
    bank = record.payee.bank_accounts.filter(is_primary=True, is_approved=True).first()
    
    if not bank or not bank.recipient_code:
        return (False, "No valid bank account for retry")
    
    # Generate new reference
    new_reference = f"RETRY-{record.id}-{uuid4().hex[:6].upper()}"
    
    # Update to pending first to release lock during network call
    payment_tx.paystack_reference = new_reference
    payment_tx.status = 'pending'
    payment_tx.failure_reason = 'Processing retry...'
    payment_tx.save()
    
    # Retry transfer (Outside transaction)
    success, transfer_code, message = paystack.initiate_transfer(
        recipient_code=bank.recipient_code,
        amount=record.net_pay,
        reference=new_reference,
        reason=f"Retry - Salary {record.payroll_period}"
    )
    
    with transaction.atomic():
        # Re-fetch to ensure we have latest state
        payment_tx.refresh_from_db()
        
        if success:
            payment_tx.transfer_code = transfer_code
            payment_tx.status = 'success'
            payment_tx.response_data = {'message': message, 'transfer_code': transfer_code, 'retry': True}
            payment_tx.save()
            
            AuditLog.objects.create(
                user=user,
                action='PAY',
                model_name='PayrollRecord',
                object_id=str(record.id),
                description=f"Retry successful: {message}"
            )
            return (True, "Payment retry successful")
        else:
            payment_tx.status = 'failed'
            payment_tx.failure_reason = message
            payment_tx.response_data = {'error': message, 'retry': True}
            payment_tx.save()
            
            AuditLog.objects.create(
                user=user,
                action='FAIL',
                model_name='PayrollRecord',
                object_id=str(record.id),
                description=f"Retry failed: {message}"
            )
            return (False, f"Retry failed: {message}")
