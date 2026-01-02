import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.conf import settings

# Create your models here.

class Warehouse(models.Model):
  warehouse_id = models.AutoField(primary_key= True)
  name = models.CharField(max_length=255)
  location = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name
  
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, editable=False, blank=True)
    vendor = models.ForeignKey(
                                    settings.AUTH_USER_MODEL, 
                                    on_delete=models.CASCADE, 
                                    related_name='products',
                                    null=True, 
                                    blank=True, 
                                    limit_choices_to={'role': 'vendor'}
                                )
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            cat_part = slugify(self.category or "GEN")[:3].upper()
            name_part = slugify(self.name)[:3].upper()
            unique_part = str(uuid.uuid4())[:4].upper()
            self.sku = f"{cat_part}-{name_part}-{unique_part}" 
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Stock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_stock_level = models.IntegerField(default=5)
    class Meta:
        unique_together = ('warehouse', 'product')

    def __str__(self):
        return f"{self.product.name} in {self.warehouse.name}: {self.quantity}"