from django.db import models
import uuid
from users.models import User
from inventory.models import Product

# Create your models here.
class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),            
        ('pending', 'Pending Approval'), 
        ('approved', 'Approved'),       
        ('rejected', 'Rejected'),       
        ('partially_converted', 'Partially PO'), 
        ('closed', 'Closed'),          
    ]

    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pr_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Kisne maanga aur kiske liye maanga
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='my_prs')
    department = models.CharField(max_length=100, null=True, blank=True) # Department tracking
    
    # Audit Fields (Zaroori hain!)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_prs')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    required_by_date = models.DateField(null=True, blank=True) # Kab tak saaman chahiye?
    
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Tracking changes

    class Meta:
        permissions = [
            ("can_approve_pr", "Can approve purchase requests"),
        ]

    def save(self, *args, **kwargs):
        if not self.pr_number:
            from django.utils import timezone
            year = timezone.now().year
            last_pr = PurchaseRequest.objects.filter(pr_number__contains=f'PR-{year}').order_by('-created_at').first()
            if last_pr:
                last_num = int(last_pr.pr_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.pr_number = f"PR-{year}-{str(new_num).zfill(4)}"
        super().save(*args, **kwargs)
    def __str__(self):
        return self.pr_number
    
class PRItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pr = models.ForeignKey(PurchaseRequest, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # PROTECT taaki product delete na ho sake
    
    specification = models.CharField(max_length=255, blank=True, help_text="Example: Grade 53, Blue Color, etc.")
    
    # Quantity maangi gayi
    requested_quantity = models.PositiveIntegerField()
    
    # Unit (Kg, Pcs, Mtr) - Ideally iska bhi ek alag model hota hai, ya fir ChoiceField
    uom = models.CharField(max_length=20, default='Pcs') 

    # Estimated Price (Manager ke hisab se kitne ka aana chahiye)
    estimated_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Tracking Fields (P2P Automation ke liye)
    # Ye field batayegi ki is item ka kitna saaman PO mein convert ho chuka hai
    ordered_quantity = models.PositiveIntegerField(default=0) 

    @property
    def pending_quantity(self):
        # Ye calculate karega kitna bacha hai
        return self.requested_quantity - self.ordered_quantity

    def __str__(self):
        return f"{self.product.name} - {self.requested_quantity} {self.uom}"
    

class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    gst_number = models.CharField(max_length=15, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00) # 1 to 5 rating

    def __str__(self):
        return self.name
    
class Quotation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pr = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='quotations')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    
    # Vendor ne kya price quote kiya aur kab tak dega
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    delivery_lead_time = models.IntegerField(help_text="Days to deliver")
    valid_until = models.DateField() # Quotation kab tak valid hai
    
    is_selected = models.BooleanField(default=False) # L1 Selection logic ke liye
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['total_amount'] # By default sabse sasta upar aayega (L1 logic)

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, related_name='quote_items', on_delete=models.CASCADE)
    pr_item = models.ForeignKey(PRItem, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent to Vendor'),
        ('partially_received', 'Partially Received'),
        ('received', 'Fully Received'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Kis PR ke against ye PO ban raha hai
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='pos')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # Audit details
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            # PO-2026-0001 format
            from django.utils import timezone
            year = timezone.now().year
            last_po = PurchaseOrder.objects.filter(po_number__contains=f'PO-{year}').order_by('-created_at').first()
            num = (int(last_po.po_number.split('-')[-1]) + 1) if last_po else 1
            self.po_number = f"PO-{year}-{str(num).zfill(4)}"
        super().save(*args, **kwargs)

class POItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, related_name='po_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField() # Final deal quantity
    unit_price = models.DecimalField(max_digits=12, decimal_places=2) # Manual deal price
    received_quantity = models.PositiveIntegerField(default=0) # Partial delivery track karne ke liye 

class GoodReciptNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grn_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Kis PO ke against saaman aaya?
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='grns')
    
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    challan_number = models.CharField(max_length=50) # Vendor ka bill/challan no.
    
    received_by = models.ForeignKey(User, on_delete=models.PROTECT)
    received_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.grn_number:
            from django.utils import timezone
            year = timezone.now().year
            last_grn = GoodReciptNote.objects.filter(grn_number__contains=f'GRN-{year}').order_by('-received_at').first()
            num = (int(last_grn.grn_number.split('-')[-1]) + 1) if last_grn else 1
            self.grn_number = f"GRN-{year}-{str(num).zfill(4)}"
        super().save(*args, **kwargs)

class GoodRecieptNoteItem(models.Model):
    grn = models.ForeignKey(GoodReciptNote, related_name='grn_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Kitna saaman truck se utra
    received_quantity = models.PositiveIntegerField()