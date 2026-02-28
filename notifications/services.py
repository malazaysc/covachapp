from django.conf import settings
from django.core.mail import send_mail

from notifications.models import UserNotification


def notify_user(user, notification_type, title, body, payload=None):
    payload = payload or {}
    UserNotification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        payload_json=payload,
    )
    send_mail(
        subject=title,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
