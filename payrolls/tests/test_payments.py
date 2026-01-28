from django.test import TestCase
from unittest.mock import patch, MagicMock
from payroll.services.recipient_service import get_bank_code, get_or_create_recipient
from payroll.models import Payee, BankAccount, TransferRecipient, PayrollRecord, PaymentTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

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
    def test_get_bank_code_resolution(self, mock_get):
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
    def test_create_recipient(self, mock_get, mock_post):
        # Mock Bank List
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "data": [{"name": "Zenith Bank", "code": "057"}]
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
        
        # Verify it was saved to DB
        self.assertTrue(TransferRecipient.objects.filter(payee=self.payee).exists())

