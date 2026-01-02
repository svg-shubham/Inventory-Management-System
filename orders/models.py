import uuid
from django.db import models
from django.conf import settings
from inventory.models import Product

class PurchaseOrder(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='purchases',
        limit_choices_to={'role': 'vendor'}
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey('inventory.Warehouse', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(help_text="Vendor ko payment kab tak karni hai")
    penalty_rate_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('received', 'Stock Received'),
        ('cancelled', 'Cancelled')
    ], default='pending')


    def __str__(self):
        return f"PO-{self.order_id}"


class SalesOrder(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='sales',
        limit_choices_to={'role': 'customer'}
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey('inventory.Warehouse', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(help_text="Customer se payment kab tak leni hai")
    order_date = models.DateTimeField(auto_now_add=True)
    penalty_rate_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Order Placed'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned')
    ], default='pending')

    def __str__(self):
        return f"SO-{self.order_id}"