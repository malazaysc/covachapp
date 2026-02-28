import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class HostProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="host_profile")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.email} ({self.status})"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="verification_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(hours=24))

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > timezone.now()
