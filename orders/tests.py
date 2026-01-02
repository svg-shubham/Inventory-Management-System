from django.urls import reverse
from rest_framework import status
from inventory.models import Stock
# Base class ko import karein (agar wo inventory app mein hai)
from inventory.test_utils import InventoryBaseTestCase 

class BusinessLogicTests(InventoryBaseTestCase):
    
    def setUp(self):
        super().setUp()
    
    def test_purchase_order_flow(self):
      from django.contrib.auth import get_user_model
      User = get_user_model()
      
      # Ek naya vendor test ke andar hi banate hain
      # Agar aapke model mein 'role' field hai toh use 'vendor' rakhein
      paisa_bolta_hai_vendor = User.objects.create_user(
          username='special_vendor', 
          password='pass',
          role='vendor' # <--- Is line ko confirm karein apne model ke hisab se
      )

      url = reverse('purchase-order-list')
      data = {
          "vendor": str(paisa_bolta_hai_vendor.pk), # Fresh PK
          "product": self.product.pk,
          "warehouse": self.warehouse.pk,
          "quantity": 100,
          "cost_price": "450.00",
          "due_date": "2026-03-20",
          "status": "pending"
      }
      
      response = self.client.post(url, data)
      
      if response.status_code != 201:
          print(f"DEBUG FINAL: {response.data}")
          
      self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sales_stock_validation(self):
        """Test: Kam stock hone par Sales order block hona chahiye"""
        # Warehouse mein sirf 10 stock dalo
        Stock.objects.create(warehouse=self.warehouse, product=self.product, quantity=10)
    
        url = reverse('salesorder-list')
        data = {
            "customer": str(self.customer.pk),
            "product": self.product.pk, # id -> pk fix
            "warehouse": self.warehouse.pk,
            "quantity": 50,
            "sell_price": "650.00",
            "due_date": "2026-02-10",
            "status": "delivered"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)