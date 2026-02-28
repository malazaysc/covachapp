from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from django.template.defaultfilters import slugify


class Amenity(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Listing(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        CONDO = "condo", "Condo"
        CABIN = "cabin", "Cabin"
        VILLA = "villa", "Villa"

    class CancellationPolicy(models.TextChoices):
        FLEXIBLE = "flexible", "Flexible"
        MODERATE = "moderate", "Moderate"
        STRICT = "strict", "Strict"

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_listings")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    property_type = models.CharField(max_length=24, choices=PropertyType.choices)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, default="United States")
    postal_code = models.CharField(max_length=20, blank=True)
    location = models.PointField(geography=True, null=True, blank=True)
    nightly_rate_usd = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.PositiveIntegerField(default=1)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    cancellation_policy = models.CharField(
        max_length=20,
        choices=CancellationPolicy.choices,
        default=CancellationPolicy.MODERATE,
    )
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "city", "nightly_rate_usd"]),
            GistIndex(fields=["location"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.host_id}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="listings/photos/", blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    @property
    def url(self):
        if self.image:
            return self.image.url
        return self.image_url

    class Meta:
        ordering = ["sort_order", "id"]


class AvailabilityBlock(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="availability_blocks")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=120, blank=True)

    class Meta:
        indexes = [models.Index(fields=["listing", "start_date", "end_date"])]
        ordering = ["start_date"]

    def __str__(self) -> str:
        return f"{self.listing.title} {self.start_date} - {self.end_date}"
