from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock  # Apne model ka naam check kar lena
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock  # Sahi model name
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Stock)
def stock_update_notification(sender, instance, **kwargs):
    # Aapke model mein 'quantity' aur 'min_stock_level' dono hain
    # Hum tab alert bhejenge jab quantity min_level se niche jaye
    if instance.quantity <= instance.min_stock_level:
        channel_layer = get_channel_layer()
        
        # Product ka naam ForeignKey se nikal rahe hain
        product_name = instance.product.name 
        warehouse_name = instance.warehouse.name
        
        async_to_sync(channel_layer.group_send)(
            "inventory_alerts",
            {
                "type": "send_notification",
                "message": f"⚠️ Low Stock: {product_name} at {warehouse_name} is only {instance.quantity} left!"
            }
        )