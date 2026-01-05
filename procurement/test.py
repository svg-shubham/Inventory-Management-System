from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from inventory.models import Product
from .models import PurchaseRequest

class PurchaseRequestTests(APITestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager_test', 
            email='manager@erp.com', 
            password='password123', 
            role='manager'
        )
        self.admin = User.objects.create_user(
            username='admin_test', 
            email='admin@erp.com', 
            password='password123', 
            role='admin'
        )
        self.product = Product.objects.create(name="Cement", sku="CMT001")
        self.client.force_authenticate(user=self.manager)

    def test_create_purchase_request(self):
        url = reverse('purchase-request-list')
        data = {
            "description": "Test PR",
            "priority": "medium",
            "items": [
                {
                    "product": self.product.pk, # .id ki jagah .pk (AttributeError fix)
                    "requested_quantity": 50,
                    "uom": "Bags",
                    "estimated_price": "400.00"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseRequest.objects.count(), 1)

    def test_approve_purchase_request(self):
        pr = PurchaseRequest.objects.create(requested_by=self.manager, description="Approve me")
        self.client.force_authenticate(user=self.admin)
        url = reverse('purchase-request-approve', kwargs={'pk': pr.pk})
        response = self.client.post(url)  
        pr.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(pr.status, 'approved')