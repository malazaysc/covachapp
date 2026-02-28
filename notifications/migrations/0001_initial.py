# Generated manually for initial project bootstrap.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("reservation_request", "Reservation Request"),
                            ("reservation_approved", "Reservation Approved"),
                            ("reservation_declined", "Reservation Declined"),
                            ("reservation_canceled", "Reservation Canceled"),
                            ("reservation_expired", "Reservation Expired"),
                            ("host_status", "Host Status"),
                        ],
                        max_length=40,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField()),
                ("payload_json", models.JSONField(blank=True, default=dict)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
