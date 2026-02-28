from django.conf import settings
from django.db import models


class UserNotification(models.Model):
    class NotificationType(models.TextChoices):
        RESERVATION_REQUEST = "reservation_request", "Reservation Request"
        RESERVATION_APPROVED = "reservation_approved", "Reservation Approved"
        RESERVATION_DECLINED = "reservation_declined", "Reservation Declined"
        RESERVATION_CANCELED = "reservation_canceled", "Reservation Canceled"
        RESERVATION_EXPIRED = "reservation_expired", "Reservation Expired"
        HOST_STATUS = "host_status", "Host Status"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=40, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    body = models.TextField()
    payload_json = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_read(self):
        return self.read_at is not None

    def __str__(self) -> str:
        return f"{self.user.email}: {self.title}"
