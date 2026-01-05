from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from inventory.models import Warehouse,Stock,Product

# Create your models here.

class ProductionBatch(models.Model):
  STATUS_CHOICES = [
    ('issued', 'Material Issued (On Floor)'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
  ]

  batch_id = models.CharField(primary_key=True, max_length=50, editable=False)
  raw_material = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="raw_batches")
  warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
  issued_quantity = models.IntegerField(help_text="Stock table se minus hone wale bundle/count")
  issued_weight = models.DecimalField(max_digits=10,decimal_places=2,help_text="Total Weight of Bundles in tones")
  issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
  issued_at = models.DateTimeField(auto_now_add=True)

  # --- PHASE 2: SHAAM (Output & Calculation) ---
  # Ye fields hum calculations ke baad update karenge for audit

  total_produced_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  total_scrap_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  process_loss = models.DecimalField(
      max_digits=10, 
      decimal_places=2, 
      default=0.00, 
      help_text="Jitna loha process mein burn/waste ho gaya"
  )
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
  completed_at = models.DateTimeField(null=True, blank=True)

  def save(self, *args, **kwargs):
        if not self.batch_id:
            # ID Logic: BAT-YYYYMMDD-Serial
            today_date = timezone.now().strftime('%Y%m%d')
            prefix = f"BAT-{today_date}-"
            last_count = ProductionBatch.objects.filter(batch_id__startswith=prefix).count()
            self.batch_id = f"{prefix}{last_count + 1:03d}"
        super().save(*args, **kwargs)

  def __str__(self):
      return f"{self.batch_id} - {self.raw_material.name}"
  
class ProductionOutput(models.Model):
    """Ek batch se nikle hue multiple items (Sheets & Scrap)"""
    batch = models.ForeignKey(ProductionBatch, related_name='outputs', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Sheet sizes or Scrap product
    
    quantity = models.IntegerField(help_text="Stock table mein plus hone wale sheets/items")
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="In products ka total weight")
    
    is_scrap = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} | {self.quantity} Nos | {self.weight}kg"
