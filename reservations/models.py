from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from listings.models import Listing


class Reservation(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        CANCELED = "canceled", "Canceled"
        EXPIRED = "expired", "Expired"

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reservations")
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guest_reservations")
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="host_reservations")
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    total_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    guest_message = models.TextField(blank=True)
    cancellation_fee_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["listing", "status", "check_in", "check_out"]),
            models.Index(fields=["host", "status", "created_at"]),
            models.Index(fields=["guest", "status", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.listing.title} ({self.guest.email})"

    @property
    def is_expired(self) -> bool:
        return self.status == self.Status.REQUESTED and self.expires_at <= timezone.now()


class ReservationEvent(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservation_events",
    )
    event_type = models.CharField(max_length=64)
    message = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
