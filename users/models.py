import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class User(AbstractUser):
    """
    Custom User model supporting UUID as primary key and 
    Role-Based Access Control (RBAC) for P2P and Sales.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = (
        ('admin', 'System Admin'),
        ('procurement', 'Procurement Officer'),
        ('inventory', 'Inventory Manager'),
        ('sales', 'Sales Executive'),
        ('finance', 'Finance Manager'),
        ('vendor', 'Vendor/Supplier'), 
        ('customer', 'Customer'),       
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='sales',
        help_text="Designated role for system access control"
    )
    email = models.EmailField(unique=True) # Industry standard: Unique email for login
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    # Helping Methods for clean Permission Checks
    @property
    def is_procurement(self):
        return self.role == 'procurement'

    @property
    def is_inventory(self):
        return self.role == 'inventory'

    @property
    def is_sales(self):
        return self.role == 'sales'

    @property
    def is_finance(self):
        return self.role == 'finance'
    
    @property
    def is_vendor(self): return self.role == 'vendor'
    
    @property
    def is_customer(self): return self.role == 'customer'

    class Meta:
        db_table = 'app_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class Notification(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    # 1. Throttling ke liye Slug (e.g., 'low-stock-cement-P001')
    # Isse hum check karenge ki kya is item ka alert hal hi mein gaya hai?
    slug = models.SlugField(max_length=255, null=True, blank=True)
    notification_type = models.CharField(max_length=50) # 'STOCK', 'APPROVAL', 'PAYMENT'
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.CharField(max_length=255,null=True,blank=True)
    priority = models.CharField(max_length=10,choices=PRIORITY_CHOICES,default="medium")
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
