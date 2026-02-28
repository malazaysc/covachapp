# Generated manually for initial project bootstrap.

import decimal
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("check_in", models.DateField()),
                ("check_out", models.DateField()),
                ("guests", models.PositiveIntegerField()),
                ("total_usd", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("approved", "Approved"),
                            ("declined", "Declined"),
                            ("canceled", "Canceled"),
                            ("expired", "Expired"),
                        ],
                        default="requested",
                        max_length=20,
                    ),
                ),
                ("guest_message", models.TextField(blank=True)),
                ("cancellation_fee_usd", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "guest",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="guest_reservations", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "host",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="host_reservations", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "listing",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reservations", to="listings.listing"),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["listing", "status", "check_in", "check_out"], name="reservations_listing_458139_idx"),
                    models.Index(fields=["host", "status", "created_at"], name="reservations_host_id_0a09d2_idx"),
                    models.Index(fields=["guest", "status", "created_at"], name="reservations_guest_i_a66f1c_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ReservationEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=64)),
                ("message", models.CharField(blank=True, max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reservation_events", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "reservation",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="reservations.reservation"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
