from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from orders.models import PurchaseOrder,SalesOrder
from inventory.models import Stock
from django.db import transaction
from finance.models import Transaction

@receiver(pre_save, sender=PurchaseOrder)
def capture_old_status(sender, instance, **kwargs):
    """
    Naye record ke liye skip karo, sirf purane record ke liye status capture karo.
    """
    if instance.pk:
        try:
            old_obj = PurchaseOrder.objects.get(pk=instance.pk)
            instance._old_status = old_obj.status
            instance._old_qty = old_obj.quantity
        except PurchaseOrder.DoesNotExist:
            instance._old_status = None
            instance._old_qty = 0
    else:
        instance._old_status = None
        instance._old_qty = 0

@receiver(post_save,sender=PurchaseOrder)
def update_stock_on_receive(sender,instance,created,**kwargs):
  # yeh chalega tab jab hum status ko receive karenge ..... status switches to received
  # Check: Kya status abhi 'received' hua hai?
  # (Agar naya bana hai aur status 'received' hai) OR (Purana status 'pending' tha aur ab 'received' hai)

  old_status = getattr(instance, '_old_status', None)
  old_qty = getattr(instance, '_old_qty', 0)
  
  change_to_apply = 0

  # Case 1: Naya Order aur status pehle se hi 'received' (POST)
  if created and instance.status == 'received':
      change_to_apply = instance.quantity

  # Case 2: Status badal kar 'received' hua (Update/PUT/PATCH)
  elif old_status != 'received' and instance.status == 'received':
      change_to_apply = instance.quantity

  # Case 3: Pehle bhi 'received' tha, ab sirf quantity update hui (Update/PUT/PATCH)
  elif old_status == 'received' and instance.status == 'received':
      change_to_apply = instance.quantity - old_qty

  # Case 4: Status 'received' se wapas 'pending' ya 'cancelled' ho gaya (Rollback)
  elif old_status == 'received' and instance.status != 'received':
      change_to_apply = -old_qty

  # Final Stock Update
  if change_to_apply != 0:
      with transaction.atomic():
          stock, _ = Stock.objects.get_or_create(
              product=instance.product,
              warehouse=instance.warehouse,
              defaults={'quantity': 0}
          )
          stock.quantity += change_to_apply
          stock.save()

@receiver(post_save, sender=SalesOrder)
def update_stock_on_sales(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_old_status', None)
    old_qty = getattr(instance, '_old_qty', 0)
    
    change_to_apply = 0 # Kitna stock change karna hai

    # CASE 1: Naya Sales Order aur status 'delivered' (rare case but handled)
    if created and instance.status == 'delivered':
        change_to_apply = -instance.quantity # Stock ghatao

    # CASE 2: Status update hoke 'delivered' hua (Most Common)
    elif old_status != 'delivered' and instance.status == 'delivered':
        change_to_apply = -instance.quantity # Stock ghatao

    # CASE 3: Pehle bhi 'delivered' tha, ab quantity badha di (e.g., 10 se 12 kar di)
    elif old_status == 'delivered' and instance.status == 'delivered':
        # Agar quantity badhi (12-10=2), toh stock 2 aur kam hona chahiye (-2)
        change_to_apply = -(instance.quantity - old_qty)

    # CASE 4: Maal wapas aa gaya (Returned)
    elif old_status == 'delivered' and instance.status == 'returned':
        change_to_apply = old_qty # Stock wapas badhao

    # Final Update
    if change_to_apply != 0:
        with transaction.atomic():
            stock, _ = Stock.objects.get_or_create(
                product=instance.product,
                warehouse=instance.warehouse
            )
            stock.quantity += change_to_apply
            stock.save()
      
@receiver(post_save, sender=PurchaseOrder)
def create_purchase_finance_record(sender, instance, created, **kwargs):
    if created:
        # SAHI FIELD NAME: cost_price
        amount = instance.quantity * instance.cost_price 
        Transaction.objects.create(
            purchase_order=instance,
            total_amount=amount,
            balance_amount=amount,
            status='unpaid'
        )

@receiver(post_save, sender=SalesOrder)
def create_sales_finance_record(sender, instance, created, **kwargs):
    if created:
        # SAHI FIELD NAME: sell_price
        amount = instance.quantity * instance.sell_price
        Transaction.objects.create(
            sales_order=instance,
            total_amount=amount,
            balance_amount=amount,
            status='unpaid'
        )