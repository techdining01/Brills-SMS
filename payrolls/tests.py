from django.test import TestCase
from unittest.mock import patch, MagicMock
from payroll.services.recipient_service import get_bank_code, get_or_create_recipient
from payroll.models import Payee, BankAccount, TransferRecipient, PayrollPeriod, PayrollRecord
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

@patch("payroll.services.recipient_service.cache")
class PaymentFixTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.payee = Payee.objects.create(
            user=self.user,
            payee_type="teacher",
            reference_code="PAY-001"
        )
        self.bank = BankAccount.objects.create(
            payee=self.payee,
            bank_name="Zenith Bank",
            account_number="1234567890",
            account_name="Test User",
            is_primary=True
        )

    @patch("payroll.services.recipient_service.requests.get")
    def test_get_bank_code_resolution(self, mock_get, mock_cache):
        # Ensure cache miss
        mock_cache.get.return_value = None
        # Mock Paystack response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": [
                {"name": "Zenith Bank", "slug": "zenith-bank", "code": "057"},
                {"name": "Guaranty Trust Bank", "slug": "guaranty-trust-bank", "code": "058"},
            ]
        }
        mock_get.return_value = mock_response

        # Test exact match
        code = get_bank_code("Zenith Bank")
        self.assertEqual(code, "057")

        # Test mapping (GTB -> Guaranty Trust Bank)
        code = get_bank_code("GTB")
        self.assertEqual(code, "058")

        # Test case insensitivity
        code = get_bank_code("zenith bank")
        self.assertEqual(code, "057")

    @patch("payroll.services.recipient_service.requests.post")
    @patch("payroll.services.recipient_service.requests.get")
    def test_create_recipient(self, mock_get, mock_post, mock_cache):
        # Ensure cache miss
        mock_cache.get.return_value = None
        # Mock Bank List
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "data": [{"name": "Zenith Bank", "code": "057", "slug": "zenith-bank"}]
        }
        mock_get.return_value = mock_get_resp

        # Mock Recipient Creation
        mock_post_resp = MagicMock()
        mock_post_resp.json.return_value = {
            "status": True,
            "data": {
                "recipient_code": "RCP_123456"
            }
        }
        mock_post.return_value = mock_post_resp

        code = get_or_create_recipient(self.payee)
        self.assertEqual(code, "RCP_123456")
        
    def test_batch_creation_flow(self, mock_cache):
        # 1. Generate Payroll
        from payroll.services.payroll_generation import bulk_generate_payroll
        
        # Ensure Period exists
        period = PayrollPeriod.objects.create(month=2, year=2025)
        
        # Ensure Payee has salary structure
        from payroll.models import SalaryStructure, SalaryComponent, SalaryStructureItem, PayeeSalaryStructure
        
        structure = SalaryStructure.objects.create(name="Basic", payee_type="teacher")
        component = SalaryComponent.objects.create(name="Basic Pay", component_type="earning", is_active=True)
        SalaryStructureItem.objects.create(salary_structure=structure, component=component, amount=50000)
        
        PayeeSalaryStructure.objects.create(payee=self.payee, salary_structure=structure)
        
        bulk_generate_payroll(period, self.user)
        
        # Verify Approval Object Created
        record = PayrollRecord.objects.get(payee=self.payee, payroll_period=period)
        self.assertTrue(hasattr(record, 'approval'), "Approval object not created")
        
        # 2. Approve Period (Mocking the view logic essentially)
        # In the view, we iterate and set approval.
        # Let's verify that WITHOUT approval, batch creation is empty?
        # Actually payment_batch_service filters by approval__admin_approved_at__isnull=False
        
        from payroll.services.payment_batch_service import create_payment_batch
        
        # Create batch BEFORE approval
        batch_1 = create_payment_batch(payroll_period=period, created_by=self.user)
        self.assertEqual(batch_1.transactions.count(), 0, "Batch should be empty before approval")
        
        # 3. Simulate View logic for approval
        record.approval.admin_approved_by = self.user
        record.approval.admin_approved_at = timezone.now()
        record.approval.save()
        
        # 4. Create batch AFTER approval
        batch_2 = create_payment_batch(payroll_period=period, created_by=self.user)
        self.assertEqual(batch_2.transactions.count(), 1, "Batch should contain transaction after approval")
