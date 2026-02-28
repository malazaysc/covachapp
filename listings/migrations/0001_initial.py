# Generated manually for initial project bootstrap.

import django.contrib.gis.db.models.fields
import django.contrib.postgres.indexes
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
            name="Amenity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Listing",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("description", models.TextField()),
                (
                    "property_type",
                    models.CharField(
                        choices=[
                            ("apartment", "Apartment"),
                            ("house", "House"),
                            ("condo", "Condo"),
                            ("cabin", "Cabin"),
                            ("villa", "Villa"),
                        ],
                        max_length=24,
                    ),
                ),
                ("street_address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("country", models.CharField(default="United States", max_length=120)),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("location", django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ("nightly_rate_usd", models.DecimalField(decimal_places=2, max_digits=10)),
                ("max_guests", models.PositiveIntegerField(default=1)),
                ("bedrooms", models.PositiveIntegerField(default=1)),
                ("bathrooms", models.DecimalField(decimal_places=1, default=1, max_digits=3)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "cancellation_policy",
                    models.CharField(
                        choices=[("flexible", "Flexible"), ("moderate", "Moderate"), ("strict", "Strict")],
                        default="moderate",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "host",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="hosted_listings", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["status", "city", "nightly_rate_usd"], name="listings_li_status_9eb9b7_idx"),
                    django.contrib.postgres.indexes.GistIndex(fields=["location"], name="listings_li_locatio_06d84d_gist"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ListingPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="listings/photos/")),
                ("caption", models.CharField(blank=True, max_length=255)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "listing",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="listings.listing"),
                ),
            ],
            options={"ordering": ["sort_order", "id"]},
        ),
        migrations.CreateModel(
            name="AvailabilityBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.CharField(blank=True, max_length=120)),
                (
                    "listing",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="availability_blocks", to="listings.listing"),
                ),
            ],
            options={
                "ordering": ["start_date"],
                "indexes": [
                    models.Index(fields=["listing", "start_date", "end_date"], name="listings_av_listing_a0165e_idx")
                ],
            },
        ),
        migrations.AddField(
            model_name="listing",
            name="amenities",
            field=models.ManyToManyField(blank=True, related_name="listings", to="listings.amenity"),
        ),
    ]
