from django.core.mail import send_mail
from django.utils import timezone
from .models import Notification
from django.conf import settings


def send_smart_notification(recipient,n_type,title,message,slug=None,priority="medium",action_url=None):
  # --- PROBLEM 1: THROTTLING (Spam Control) ---
    if slug:
        two_hours_ago = timezone.now() - timezone.timedelta(hours=2)
        recent_notif = Notification.objects.filter(
            recipient=recipient, 
            slug=slug, 
            created_at__gte=two_hours_ago
        ).exists()
        
        if recent_notif:
            return None # 2 ghante ke andar same alert nahi bhejenge

    # --- SAVE TO DATABASE ---
    notif = Notification.objects.create(
        recipient=recipient,
        notification_type=n_type,
        title=title,
        message=message,
        slug=slug,
        priority=priority,
        action_url=action_url
    )

    # --- PROBLEM 3: EMAIL INTEGRATION (Urgent Only) ---
    if priority == 'urgent' or priority == 'high':
        try:
            # send_mail(
            #     subject=f"[ERP ALERT] {title}",
            #     message=message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[recipient.email],
            #     fail_silently=True,
            # )
            # notif.is_emailed = True
            # notif.save()
            print("Notification email send via email")
        except Exception as e:
            print(f"Email Error: {e}")

    # --- PROBLEM 2: REAL-TIME (Django Channels Hint) ---
    # Yahan hum Channels ka group_send() call karenge future mein
    # Taki bina refresh kiye browser par popup aa jaye.
    
    return notif