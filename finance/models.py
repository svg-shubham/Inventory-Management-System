import uuid
from django.db import models
from django.core.validators import MinValueValidator
from orders.models import PurchaseOrder, SalesOrder

class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, null=True, blank=True, related_name='finance')
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, null=True, blank=True, related_name='finance')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Base Order Amount")
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount_cache = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue')
    ], default='unpaid')

    updated_at = models.DateTimeField(auto_now=True)

    def update_balance(self):
        """Har payment ke baad balance refresh karne ke liye method"""
        # Sabhi related payments ka sum nikalna
        total_paid = sum(p.amount_paid for p in self.payment_logs.all())
        self.paid_amount_cache = total_paid
        self.balance_amount = (self.total_amount + self.penalty_amount) - total_paid
        
        if self.balance_amount <= 0:
            self.status = 'paid'
        elif total_paid > 0:
            self.status = 'partial'
        
        self.save()
        
    def update_penalty(self):
        # Yeh logic aapki deri par penalty calculate karega
        from datetime import date
        order = self.purchase_order or self.sales_order
        if order and date.today() > order.due_date:
            days_late = (date.today() - order.due_date).days
            self.penalty_amount = days_late * order.penalty_rate_day
            self.save()

    def __str__(self):
        return f"Account for {self.purchase_order or self.sales_order}"

class PaymentLog(models.Model):
    """Har ek installment/paisa jo aata ya jata hai uska detailed record"""
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payment_logs')
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_mode = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('upi', 'UPI/PhonePe/GPay'),
        ('bank_transfer', 'NEFT/IMPS'),
        ('cheque', 'Cheque')
    ])
    
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Txn ID or Cheque No.")
    payment_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.transaction.update_balance()

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.transaction.transaction_id}"