from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .forms import SalaryComponentForm 

from .models import (
    Payee, BankAccount, PayrollPeriod, PayrollRecord,
    PayrollLineItem, PaymentTransaction,
    AuditLog, SalaryComponent
)
from django.conf import settings
from .forms import (
    PayeeForm, BankAccountForm, SalaryStructureForm, SalaryItemFormSet, 
    PayrollGenerationForm, SalaryComponentForm, PayeeSalaryStructureForm
)
from .admin_forms import AdminPayeeCreationForm
from .utils import get_loan_deduction, notify_payee_payment_success
from .paystack_service import process_payroll_payments, retry_failed_payment, PaystackService
from decimal import Decimal


@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def edit_payee_salary_structure(request, payee_id):
    payee = get_object_or_404(Payee, id=payee_id)
    assignment = getattr(payee, 'salary_assignment', None)
    
    if request.method == 'POST':
        form = PayeeSalaryStructureForm(request.POST, instance=assignment)
        if form.is_valid():
            new_assignment = form.save(commit=False)
            new_assignment.payee = payee
            new_assignment.save()
            messages.success(request, f"Salary structure updated for {payee.user.get_full_name()}")
            return redirect('payroll:admin_payee_list')
    else:
        form = PayeeSalaryStructureForm(instance=assignment)
    
    return render(request, 'payroll/admin/edit_payee_structure.html', {
        'form': form,
        'payee': payee
    })

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def retry_payroll_record(request, record_id):
    record = get_object_or_404(PayrollRecord, id=record_id)
    period = record.payroll_period
    payee = record.payee
    
    if period.is_locked:
        messages.error(request, "Cannot retry payroll for a locked period.")
        return redirect('payroll:payroll_detail', period_id=period.id)
    
    error_msg = None
    if not payee.has_salary_structure():
        error_msg = "Missing salary structure"
    elif not payee.has_primary_bank():
        error_msg = "No primary bank account assigned"
    
    if error_msg:
        record.is_processed = False
        record.processing_error = error_msg
        record.save()
        messages.error(request, f"Retry failed for {payee.user.get_full_name()}: {error_msg}")
        return redirect('payroll:payroll_detail', period_id=period.id)
        
    try:
        structure = payee.salary_assignment.salary_structure
        gross_pay = Decimal("0.00")
        line_item_deductions = Decimal("0.00")
        
        record.line_items.all().delete()
        
        for item in structure.items.all():
            comp_amount = item.amount 
            is_earning = (item.component.component_type == 'earning')
            
            if is_earning:
                gross_pay += comp_amount
            else:
                line_item_deductions += comp_amount
            
            PayrollLineItem.objects.create(
                payroll_record=record,
                name=item.component.name,
                amount=comp_amount,
                is_deduction=not is_earning
            )
        
        tax_deductions = Decimal("0.00")
        if structure.is_taxable:
            tax_deductions = (gross_pay * structure.tax_rate) / Decimal("100")

        record.gross_pay = gross_pay
        record.loan_deductions = get_loan_deduction(payee, period.month, period.year)
        record.tax_deductions = tax_deductions 
        record.other_deductions = line_item_deductions
        
        record.calculate_net_pay()
        record.is_processed = True
        record.processing_error = None
        record.save()
        messages.success(request, f"Payroll re-generated successfully for {payee.user.get_full_name()}.")
    except Exception as e:
        record.is_processed = False
        record.processing_error = str(e)
        record.save()
        messages.error(request, f"Retry failed for {payee.user.get_full_name()}: {str(e)}")
        
    return redirect('payroll:payroll_detail', period_id=period.id)

@login_required
def dashboard(request):
    if request.user.role in ['admin', 'staff'] or request.user.is_superuser:
        return admin_dashboard(request)
    else:
        return payee_dashboard(request)

def admin_dashboard(request):
    periods = PayrollPeriod.objects.filter(is_locked=True).order_by('-year', '-month')[:6]
    labels = [str(p) for p in reversed(periods)]
    
    data = []
    for p in reversed(periods):
        total = PayrollRecord.objects.filter(payroll_period=p).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        data.append(float(total))
        
    chart_data = {
        'labels': labels,
        'data': data
    }
    
    pending_banks = BankAccount.objects.filter(is_approved=False).count()
    
    return render(request, 'payroll/admin_dashboard.html', {
        'chart_data': json.dumps(chart_data),
        'pending_banks': pending_banks
    })

def payee_dashboard(request):
    try:
        payee = request.user.payee_profile
    except Payee.DoesNotExist:
        payee = None
        
    recent_payslips = []
    if payee:
        recent_payslips = PayrollRecord.objects.filter(payee=payee).order_by('-created_at')[:5]
        
    return render(request, 'payroll/payee_dashboard.html', {
        'payee': payee,
        'recent_payslips': recent_payslips
    })


@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def admin_create_payee(request):
    if request.method == 'POST':
        form = AdminPayeeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payee created successfully.')
            return redirect('payroll:admin_payee_list')
    else:
        form = AdminPayeeCreationForm()

    return render(request, 'payroll/admin_create_payee.html', {'form': form})


@login_required
def manage_bank_account(request):
    try:
        payee = Payee.objects.get(user=request.user)
        accounts = payee.bank_accounts.all()
        if request.method == 'POST':
            form = BankAccountForm(request.POST)
            if form.is_valid():
                account = form.save(commit=False)
                account.payee = payee
                account.save()
                messages.info(request, 'Bank account added. Waiting for Admin approval.')
                return redirect('payroll:manage_bank_account')
        else:
            form = BankAccountForm()
    except Payee.DoesNotExist:
        messages.error(request, 'You do not have a payroll profile.')
        return redirect('payroll:payee_profile')

    return render(request, 'payroll/bank_accounts.html', {'form': form, 'accounts': accounts})



from .admin_forms import AdminBankAccountForm

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def admin_manage_bank_account(request):
    """Allow admin to manage bank accounts for all payees."""
    # Get all payees' bank accounts
    all_accounts = BankAccount.objects.select_related('payee', 'payee__user').order_by('account_name')
    
    if request.method == 'POST':
        form = AdminBankAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank account added successfully.')
            return redirect('payroll:admin_manage_bank_account')
    else:
        form = AdminBankAccountForm()
    
    return render(request, 'payroll/admin_bank_accounts.html', {
        'form': form,
        'accounts': all_accounts
    })


@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def approve_bank_accounts(request):
    pending_accounts = BankAccount.objects.filter(is_approved=False)
    
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        action = request.POST.get('action')
        account = get_object_or_404(BankAccount, id=account_id)
        
        if action == 'approve':
            account.is_approved = True
            account.save()
            messages.success(request, f"Approved {account}")
        elif action == 'reject':
            account.delete()
            messages.warning(request, "Rejected bank account.")
            
        return redirect('payroll:approve_bank_accounts')
        
    return render(request, 'payroll/approve_bank_accounts.html', {'accounts': pending_accounts})

@login_required
def payee_profile(request):
    payee = Payee.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = PayeeForm(request.POST, instance=payee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:dashboard_redirect')
    else:
        form = PayeeForm(instance=payee)
        
    return render(request, 'payroll/payee_profile.html', {'form': form, 'payee': payee})


@login_required 
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def create_salary_structure(request):
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST)
        formset = SalaryItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            structure = form.save()
            formset.instance = structure
            formset.save()
            messages.success(request, 'Salary Structure Created.')
            return redirect('payroll:payroll_list') 
    else:
        form = SalaryStructureForm()
        formset = SalaryItemFormSet()
        
    return render(request, 'payroll/create_structure.html', {'form': form, 'formset': formset})


@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def manage_salary_components(request):
    components = SalaryComponent.objects.filter(is_active=True)
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Component added.')
            return redirect('payroll:manage_salary_components')
    else:
        form = SalaryComponentForm()
    return render(request, 'payroll/admin/manage_components.html', {'form': form, 'components': components})


@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def generate_payroll(request):
    if request.method == 'POST':
        form = PayrollGenerationForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)
            if PayrollPeriod.objects.filter(month=period.month, year=period.year).exists():
                period = PayrollPeriod.objects.get(month=period.month, year=period.year)
                if period.is_locked:
                    messages.error(request, 'This period is locked.')
                    return redirect('payroll:payroll_list')
            else:
                period.save()
            
            payees = Payee.objects.filter(is_active=True)
            if not payees.exists():
                messages.warning(request, 'No active payees found. Please onboard staff first.')
                return redirect('payroll:generate_payroll')

            count = 0
            skipped_payees = []
            for payee in payees:
                error_msg = None
                if not payee.has_salary_structure():
                    error_msg = "Missing salary structure"
                elif not payee.has_primary_bank():
                    error_msg = "No primary bank account assigned"
                
                record, created = PayrollRecord.objects.get_or_create(payee=payee, payroll_period=period)
                
                if error_msg:
                    record.is_processed = False
                    record.processing_error = error_msg
                    record.save()
                    skipped_payees.append(f"{payee.user.get_full_name()} ({error_msg})")
                    continue
                
                try:
                    structure = payee.salary_assignment.salary_structure
                    gross_pay = Decimal("0.00")
                    line_item_deductions = Decimal("0.00")
                    
                    record.line_items.all().delete()
                    
                    for item in structure.items.all():
                        comp_amount = item.amount 
                        is_earning = (item.component.component_type == 'earning')
                        
                        if is_earning:
                            gross_pay += comp_amount
                        else:
                            line_item_deductions += comp_amount
                        
                        PayrollLineItem.objects.create(
                            payroll_record=record,
                            name=item.component.name,
                            amount=comp_amount,
                            is_deduction=not is_earning
                        )
                    
                    # Calculate tax at package level
                    tax_deductions = Decimal("0.00")
                    if structure.is_taxable:
                        tax_deductions = (gross_pay * structure.tax_rate) / Decimal("100")

                    record.gross_pay = gross_pay
                    record.loan_deductions = get_loan_deduction(payee, period.month, period.year)
                    record.tax_deductions = tax_deductions 
                    record.other_deductions = line_item_deductions
                    
                    record.calculate_net_pay()
                    record.is_processed = True
                    record.processing_error = None
                    record.save()
                    count += 1
                except Exception as e:
                    record.is_processed = False
                    record.processing_error = str(e)
                    record.save()
                    skipped_payees.append(f"{payee.user.get_full_name()} (Error: {str(e)})")
            
            if count == 0:
                messages.warning(request, f'No payroll records successfully generated. Reasons: {", ".join(skipped_payees)}')
                return redirect('payroll:generate_payroll')

            period.is_generated = True
            period.save()
            msg = f'Payroll Generated for {count} payees.'
            if skipped_payees:
                msg += f' {len(skipped_payees)} payees were skipped due to errors.'
            messages.success(request, msg)
            return redirect('payroll:payroll_detail', period_id=period.id)
    else:
        form = PayrollGenerationForm()
    
    payee_count = Payee.objects.filter(is_active=True).count()
    return render(request, 'payroll/generate_payroll.html', {'form': form, 'payee_count': payee_count})


@login_required
def payroll_list(request):
    periods = PayrollPeriod.objects.all()
    return render(request, 'payroll/period_list.html', {'periods': periods})

@login_required
def payroll_detail(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    # Sync payees: Ensure all active payees have a record in this period if it's not locked
    if not period.is_locked:
        active_payees = Payee.objects.filter(is_active=True)
        for payee in active_payees:
            PayrollRecord.objects.get_or_create(payee=payee, payroll_period=period)
            
    records = period.records.all().select_related('payee__user')
    return render(request, 'payroll/period_detail.html', {'period': period, 'records': records})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def approve_lock_payroll(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    if not period.is_locked:
        period.is_locked = True
        period.is_approved_by_admin = True
        period.save()
        messages.success(request, f"Payroll Period {period} Approved and Locked.")
    return redirect('payroll:payroll_detail', period_id=period.id)

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff'] or u.is_superuser)
def admin_payee_list(request):
    q = request.GET.get('q', '')
    if q:
        payees = Payee.objects.filter(
            models.Q(user__first_name__icontains=q) |
            models.Q(user__last_name__icontains=q) |
            models.Q(reference_code__icontains=q)
        ).select_related('user')
    else:
        payees = Payee.objects.all().select_related('user')
    
    return render(request, 'payroll/admin/payee_list.html', {'payees': payees})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def toggle_payee_status(request, payee_id):
    payee = get_object_or_404(Payee, id=payee_id)
    payee.is_active = not payee.is_active
    payee.save()
    status = "activated" if payee.is_active else "deactivated"
    messages.success(request, f"Payee {payee.user.get_full_name()} has been {status}.")
    return redirect('payroll:admin_payee_list')

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def delete_payee(request, payee_id):
    payee = get_object_or_404(Payee, id=payee_id)
    name = payee.user.get_full_name()
    payee.delete()
    messages.success(request, f"Payee {name} has been deleted.")
    return redirect('payroll:admin_payee_list')


@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def delete_payroll_record(request, record_id):
    record = get_object_or_404(PayrollRecord, id=record_id)
    period_id = record.payroll_period.id
    
    if record.payroll_period.is_locked:
        messages.error(request, "Cannot delete record from a locked period.")
    else:
        name = record.payee.user.get_full_name()
        record.delete()
        messages.success(request, f"Removed {name} from this payroll period.")
    return redirect('payroll:payroll_detail', period_id=period_id)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def delete_payroll_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    if period.is_locked:
        messages.error(request, "Cannot delete a locked payroll period.")
    else:
        period_str = str(period)
        # Delete associated records first to avoid ProtectedError
        period.records.all().delete()
        period.delete()
        messages.success(request, f"Payroll period {period_str} has been deleted.")
    
    return redirect('payroll:payroll_list')



@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def process_payments(request, period_id):
    """Initiate Paystack transfers for a payroll period."""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    if not period.is_locked:
        messages.error(request, "Period must be approved and locked before processing payments.")
        return redirect('payroll:payroll_detail', period_id=period.id)
    
    try:
        batch, success_count, failed_records = process_payroll_payments(period, request.user)
        
        if success_count > 0:
            messages.success(request, f"✓ {success_count} payments initiated successfully!")
        
        if failed_records:
            messages.warning(request, f"⚠ {len(failed_records)} payments failed. See details below.")
        
        return redirect('payroll:payment_status', period_id=period.id)
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('payroll:payroll_detail', period_id=period.id)
    except Exception as e:
        messages.error(request, f"Error processing payments: {str(e)}")
        return redirect('payroll:payroll_detail', period_id=period.id)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def payment_status(request, period_id):
    """Show payment status with success/failed transactions."""
    period = get_object_or_404(PayrollPeriod, id=period_id)
    
    # Get all transactions for this period
    records = period.records.select_related('payee', 'payee__user').prefetch_related('transactions')
    
    payment_data = []
    success_count = 0
    failed_count = 0
    idle_count = 0
    
    for record in records:
        latest_tx = record.transactions.order_by('-created_at').first()
        status = latest_tx.status if latest_tx else 'not_initiated'
        
        # Determine failure reason if idle/failed
        failure_reason = None
        if not latest_tx:
            idle_count += 1
            # Check why it wasn't initiated
            bank = record.payee.bank_accounts.filter(is_primary=True).first()
            if not bank:
                failure_reason = "No primary bank account"
            elif not bank.is_approved:
                failure_reason = "Bank account not approved"
            else:
                failure_reason = "Ready for processing"
        elif status == 'failed':
            failed_count += 1
            failure_reason = latest_tx.failure_reason or "Transfer failed at Paystack"
        elif status == 'success':
            success_count += 1

        payment_data.append({
            'record': record,
            'transaction': latest_tx,
            'status': status,
            'failure_reason': failure_reason,
            'can_retry': latest_tx and latest_tx.status == 'failed',
            'can_process': not latest_tx and failure_reason == "Ready for processing"
        })
    
    return render(request, 'payroll/payment_status.html', {
        'period': period,
        'payment_data': payment_data,
        'success_count': success_count,
        'failed_count': failed_count,
        'idle_count': idle_count
    })
    

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
@require_POST
def retry_payment(request, transaction_id):
    """Retry a failed payment."""
    success, message = retry_failed_payment(transaction_id, request.user)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    # Get period from transaction
    tx = get_object_or_404(PaymentTransaction, id=transaction_id)
    return redirect('payroll:payment_status', period_id=tx.payroll_record.payroll_period.id)

@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhook notifications."""
    
    # Verify signature
    if not PaystackService.verify_webhook_signature(request):
        return HttpResponse(status=400)
    
    try:
        payload = json.loads(request.body)
        event = payload.get('event')
        data = payload.get('data', {})
        
        if event == 'transfer.success':
            # Update transaction status
            reference = data.get('reference')
            if reference:
                try:
                    tx = PaymentTransaction.objects.get(paystack_reference=reference)
                    tx.status = 'success'
                    tx.response_data = data
                    tx.save()
                    
                    # Notify payee via Telegram
                    notify_payee_payment_success(tx)
                    
                    AuditLog.objects.create(
                        user=None,
                        action='UPDATE',
                        model_name='PaymentTransaction',
                        object_id=str(tx.id),
                        description=f"Webhook: Transfer successful - {reference}"
                    )
                except PaymentTransaction.DoesNotExist:
                    pass
        
        elif event == 'transfer.failed':
            reference = data.get('reference')
            if reference:
                try:
                    tx = PaymentTransaction.objects.get(paystack_reference=reference)
                    tx.status = 'failed'
                    tx.failure_reason = data.get('reason', 'Transfer failed')
                    tx.response_data = data
                    tx.save()
                    
                    AuditLog.objects.create(
                        user=None,
                        action='FAIL',
                        model_name='PaymentTransaction',
                        object_id=str(tx.id),
                        description=f"Webhook: Transfer failed - {data.get('reason')}"
                    )
                except PaymentTransaction.DoesNotExist:
                    pass
        
        return HttpResponse(status=200)
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return HttpResponse(status=400)

@login_required
def payslip_view(request, record_id):
    record = get_object_or_404(PayrollRecord, id=record_id)
    
    # Allow access if:
    # 1. User is an admin or staff member
    # 2. User is a superuser
    # 3. record belongs to the user
    is_admin_or_staff = request.user.role in ['admin', 'teacher'] or request.user.is_superuser
    is_owner = record.payee.user == request.user
    
    if not (is_admin_or_staff or is_owner):
         messages.error(request, "Unauthorized access.")
         return redirect('accounts:dashboard_redirect')
    
    
    return render(request, 'payroll/payslip.html', {
        'record': record,
        'SCHOOL_NAME': settings.SCHOOL_NAME,
        'SCHOOL_ADDRESS': settings.SCHOOL_ADDRESS,
        'SCHOOL_LOGO_PATH': settings.SCHOOL_LOGO_PATH
    })
