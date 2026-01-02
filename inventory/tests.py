# Create your tests here.
# inventory/tests.py

from django.urls import reverse
from rest_framework import status
from .models import Warehouse, Product, Stock
# Humne jo Base class banayi thi use import karein
from .test_utils import InventoryBaseTestCase 

class InventoryTests(InventoryBaseTestCase):
    
    def setUp(self):
        super().setUp()
    
    def test_warehouse_crud(self):
        """Test Warehouse creation and retrieval"""
        # Note: 'warehouse-list' naam check kar lena urls.py mein (router basename)
        url = reverse('warehouse-list-create') 
        data = {"name": "Islapur Branch", "location": "Nanded"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 1 setup mein bana tha + 1 abhi = 2
        self.assertEqual(Warehouse.objects.count(), 2)

    def test_add_stock_custom_action(self):
        """Test custom POST /stocks/{id}/add_stock/"""
        stock = Stock.objects.create(
            warehouse=self.warehouse, 
            product=self.product, 
            quantity=10
        )
        # Custom action ka URL format: 'modelname-actionname'
        url = reverse('stock-add-stock', kwargs={'pk': stock.id})
        response = self.client.post(url, {"added_quantity": 50})
        
        stock.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(stock.quantity, 60)