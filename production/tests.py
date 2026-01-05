from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from decimal import Decimal
from inventory.models import Product, Warehouse, Stock
from production.models import ProductionBatch

User = get_user_model()

class ProductionAPITests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # 1. User Setup: Ise Superuser + Staff + Manager Role teeno de dete hain
        self.user = User.objects.create_superuser(
            username='admin_final', 
            password='password123', 
            email='admin_final@test.com'
        )
        # Ensure role field exists and match your permission class check
        if hasattr(self.user, 'role'):
            self.user.role = 'InventoryManager' 
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        # 2. Master Data
        self.raw_material = Product.objects.create(name="Steel Coil", sku="RAW-001")
        self.finished_good = Product.objects.create(name="Steel Sheet", sku="FIN-001")
        self.warehouse = Warehouse.objects.create(name="Main Unit")
        
        # Initial Stock: 10 units
        self.stock = Stock.objects.create(
            product=self.raw_material, 
            warehouse=self.warehouse, 
            quantity=10
        )
        
        self.list_url = '/production/batches/'

    def test_create_batch_success(self):
        """Test: Batch banna chahiye aur stock 10 se 8 hona chahiye"""
        self.client.force_authenticate(user=self.user)
        payload = {
            "raw_material": self.raw_material.pk,
            "warehouse": self.warehouse.pk,
            "issued_quantity": 2,
            "issued_weight": "200.00"
        }
        # Yahan hum format='json' specify kar rahe hain jo aksar 403/415 se bachata hai
        response = self.client.post(self.list_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 8)

    def test_complete_batch_calculation(self):
        """Test: Process Loss calculation (1000 - 940.75 = 59.25)"""
        batch = ProductionBatch.objects.create(
            raw_material=self.raw_material,
            warehouse=self.warehouse,
            issued_quantity=1,
            issued_weight=Decimal('1000.00'),
            issued_by=self.user,
            status='issued'
        )
        
        self.client.force_authenticate(user=self.user)
        complete_url = f"{self.list_url}{batch.pk}/complete/"
        
        payload = {
            "outputs": [
                {"product": self.finished_good.pk, "quantity": 10, "weight": "900.50", "is_scrap": False},
                {"product": self.finished_good.pk, "quantity": 1, "weight": "40.25", "is_scrap": True}
            ]
        }
        
        response = self.client.patch(complete_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data['process_loss'])), Decimal('59.25'))

    def test_create_batch_insufficient_stock(self):
        """Test: Stock kam hone par validation error"""
        self.client.force_authenticate(user=self.user)
        payload = {
            "raw_material": self.raw_material.pk,
            "warehouse": self.warehouse.pk,
            "issued_quantity": 50,
            "issued_weight": "5000.00"
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_complete_twice(self):
        """Test: Status check logic (Already completed batch)"""
        batch = ProductionBatch.objects.create(
            raw_material=self.raw_material,
            warehouse=self.warehouse,
            issued_quantity=1,
            issued_weight=Decimal('100.00'),
            issued_by=self.user,
            status='completed'
        )
        
        self.client.force_authenticate(user=self.user)
        complete_url = f"{self.list_url}{batch.pk}/complete/"
        response = self.client.patch(complete_url, {"outputs": []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_worker_permission_denied(self):
        """Worker role check"""
        worker = User.objects.create_user(username='worker_only', password='123', role='Worker')
        # Worker ko is_staff nahi banayenge
        self.client.force_authenticate(user=worker)
        response = self.client.post(self.list_url, {"raw_material": self.raw_material.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)