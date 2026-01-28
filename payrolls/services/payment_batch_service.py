from payroll.models import (
    PaymentBatch,
    PaymentTransaction,
    PayrollRecord,
)


def create_payment_batch(*, payroll_period, created_by):
    batch = PaymentBatch.objects.create(
        payroll_period=payroll_period,
        created_by=created_by,
    )

    records = PayrollRecord.objects.filter(
        payroll_period=payroll_period,
        approval__admin_approved_at__isnull=False,
    ).select_related("payee")

    for record in records:
        bank = record.payee.bank_accounts.filter(is_primary=True).first()

        PaymentTransaction.objects.create(
            payroll_record=record,
            batch=batch,
            amount=record.net_pay,
            bank_name=bank.bank_name,
            account_number=bank.account_number,
            account_name=bank.account_name,
        )

    return batch
