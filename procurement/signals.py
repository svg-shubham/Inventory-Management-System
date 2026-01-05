from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GoodRecieptNoteItem
from inventory.models import Stock # Aapka main inventory table

@receiver(post_save, sender=GoodRecieptNoteItem)
def update_stock_and_po_status(sender, instance, created, **kwargs):
    if created:
        # 1. Update Inventory Stock
        stock, _ = Stock.objects.get_or_create(
            product=instance.product,
            warehouse=instance.grn.purchase_order.purchase_request.items.first().warehouse # Maan lo PR se warehouse mil raha hai
        )
        stock.quantity += instance.received_quantity
        stock.save()

        # 2. Update PO Item 'received_quantity'
        po_item = instance.grn.purchase_order.po_items.get(product=instance.product)
        po_item.received_quantity += instance.received_quantity
        po_item.save()

        # 3. Check if PO is fully completed
        total_ordered = sum(item.quantity for item in instance.grn.purchase_order.po_items.all())
        total_received = sum(item.received_quantity for item in instance.grn.purchase_order.po_items.all())

        po = instance.grn.purchase_order
        if total_received >= total_ordered:
            po.status = 'received'
        else:
            po.status = 'partially_received'
        po.save()