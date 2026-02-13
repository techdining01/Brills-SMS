import requests
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def get_loan_deduction(payee, month, year):
    """
    Calculate the total loan deduction for a payee in a given month/year.
    """
    from loans.models import LoanApplication
    
    # Get all approved loans for this payee that still have a balance
    loans = LoanApplication.objects.filter(
        payee=payee, 
        status='approved',
        outstanding_balance__gt=0
    )
    
    total_deduction = Decimal('0.00')
    for loan in loans:
        # If remaining balance is less than monthly deduction, take only the balance
        deduction = min(loan.monthly_deduction, loan.outstanding_balance)
        total_deduction += deduction
            
    return total_deduction

def send_telegram_notification(message):
    """
    Sends a notification message to a Telegram chat via a Bot.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in settings.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        logger.warning("Telegram Bot Token or Chat ID not configured. Notification skipped.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False

def notify_payee_payment_success(transaction):
    """
    Specific notification for a successful payroll payment.
    """
    record = transaction.payroll_record
    payee = record.payee
    user = payee.user
    
    payee_name = user.get_full_name() if user else "Payee"
    amount = transaction.amount
    period = record.payroll_period
    
    message = (
        f"<b>Payment Successful!</b>\n\n"
        f"Hello {payee_name},\n"
        f"Your payment for <b>{period}</b> has been processed successfully.\n\n"
        f"<b>Amount:</b> {settings.CURRENCY_SYMBOL}{amount:,.2f}\n"
        f"<b>Reference:</b> {transaction.paystack_reference}\n"
        f"<b>Status:</b> PAID\n\n"
        f"Thank you for your service to {settings.SCHOOL_NAME}!"
    )
    
    return send_telegram_notification(message)
