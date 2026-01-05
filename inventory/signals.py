from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Stock
from users.utils import send_smart_notification  # Humara naya helper
from users.models import User

@receiver(post_save, sender=Stock)
def stock_update_notification(sender, instance, **kwargs):
    # Condition wahi purani: jab stock min_level se niche jaye
    if instance.quantity <= instance.min_stock_level:
        
        # --- 1. AAPKA EXISTING LOGIC (Bina chede) ---
        channel_layer = get_channel_layer()
        product_name = instance.product.name 
        warehouse_name = instance.warehouse.name
        
        async_to_sync(channel_layer.group_send)(
            "inventory_alerts",
            {
                "type": "send_notification",
                "message": f"⚠️ Low Stock: {product_name} at {warehouse_name} is only {instance.quantity} left!"
            }
        )

        # --- 2. NAYA SMART LOGIC (Throttling aur Email ke liye) ---
        # Sabhi active inventory managers ko dhoondo
        inventory_managers = User.objects.filter(role='inventory', is_active=True)
        
        for manager in inventory_managers:
            # Throttling Slug: Har product aur manager ke liye unique
            # Isse WebSockets har baar chalega, par Email aur DB record 2 ghante mein ek baar
            notif_slug = f"low-stock-{instance.product.pk}-{manager.id}"
            
            send_smart_notification(
                recipient=manager,
                n_type='STOCK_ALERT',
                title=f"Low Stock Alert: {product_name}",
                message=f"Stock for {product_name} at {warehouse_name} is only {instance.quantity}. Immediate action required.",
                slug=notif_slug,
                priority='high', # Isse automatic email jayega
                action_url=f"/inventory/stock/{instance.id}/"
            )