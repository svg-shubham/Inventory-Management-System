from django.urls import reverse
from rest_framework import status
from inventory.test_utils import InventoryBaseTestCase
from .models import Transaction

class FinanceTests(InventoryBaseTestCase):

    def test_payment_updates_transaction_balance(self):
        """Test: Kya payment karne par balance automatically ghat raha hai?"""
        
        # 1. Ek dummy account setup karo
        txn = Transaction.objects.create(
            total_amount=1000, 
            balance_amount=1000, 
            status='unpaid'
        )
        
        # 2. Payment entry post karo
        url = reverse('paymentlog-list') # payment-log-list check kar lena router name
        payload = {
            "transaction": str(txn.transaction_id),
            "amount_paid": "400.00",
            "payment_mode": "upi",
            "remarks": "Test Payment"
        }
        response = self.client.post(url, payload)
        
        # Check: Kya API ne 'Success' bola?
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Database se fresh data uthao
        txn.refresh_from_db()
        
        # Check: Kya math sahi hai? (1000 - 400 = 600)
        self.assertEqual(float(txn.balance_amount), 600.0)
        
        # Check: Kya status update hua?
        self.assertEqual(txn.status, 'partial')