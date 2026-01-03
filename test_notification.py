import os
import django
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# 1. Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yogesh_inventory.settings')
django.setup()

def send_test_alert():
    channel_layer = get_channel_layer()
    print("Sending notification...")
    
    async_to_sync(channel_layer.group_send)(
        "inventory_alerts", 
        {
            "type": "send_notification",
            "message": "🔥 Success! Script se notification aa gayi!"
        }
    )
    print("Done! Check your browser.")

if __name__ == "__main__":
    send_test_alert()