from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from inventory.models import Warehouse, Product

User = get_user_model()

class InventoryBaseTestCase(APITestCase):
    def setUp(self):
        # 1. Admin/User Setup
        self.admin_user = User.objects.create_superuser(username='admin_test', password='password123')
        self.vendor = User.objects.create_user(username='vendor_test', password='password123')
        self.customer = User.objects.create_user(username='customer_test', password='password123')
        
        self.client.force_authenticate(user=self.admin_user)
        
        # 2. Objects Setup (Ye wahi variables hain jo 'AttributeError' de rahe the)
        self.warehouse = Warehouse.objects.create(name="Test Warehouse", location="Test Loc")
        self.product = Product.objects.create(name="Test Product", vendor=self.vendor)
        
        # IMPORTANT: Child classes ke liye super call
        super().setUp()