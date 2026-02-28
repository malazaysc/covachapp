import sqlite3
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.utils import timezone

from accounts.models import HostProfile
from listings.models import Amenity, AvailabilityBlock, Listing, ListingPhoto
from notifications.models import UserNotification
from reservations.models import Reservation

SAMPLE_DB = Path(__file__).resolve().parents[3] / "sample-data.db"

PROPERTY_TYPE_MAP = {
    "Apartment": "apartment",
    "Loft": "apartment",
    "Penthouse": "apartment",
    "Studio": "apartment",
    "Townhouse": "apartment",
    "House": "house",
    "Bungalow": "house",
    "Cottage": "house",
    "Condo": "condo",
    "Villa": "villa",
}

BOOKING_STATUS_MAP = {
    "confirmed": "approved",
    "pending": "requested",
    "cancelled": "canceled",
}


class Command(BaseCommand):
    help = "Seed demo data from sample SQLite database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Skip seeding when application data already exists",
        )

    def handle(self, *args, **options):
        if not SAMPLE_DB.exists():
            self.stderr.write(self.style.ERROR(f"Sample DB not found: {SAMPLE_DB}"))
            return

        if options["if_empty"] and self._is_populated():
            self.stdout.write(self.style.WARNING("Application data already exists. Skipping demo seed."))
            return

        conn = sqlite3.connect(str(SAMPLE_DB))
        conn.row_factory = sqlite3.Row

        if options["flush"]:
            self._flush()

        User = get_user_model()

        # 1. Create test users
        self.stdout.write("Creating users...")
        self._create_user(User, "ops@covach.dev", is_staff=True)
        guest = self._create_user(User, "guest@covach.dev")

        hosts = []
        for i in range(1, 6):
            host = self._create_user(User, f"host{i}@covach.dev")
            HostProfile.objects.get_or_create(
                user=host,
                defaults={"status": HostProfile.Status.APPROVED, "bio": f"Demo host {i}"},
            )
            hosts.append(host)

        # 2. Create amenities
        self.stdout.write("Creating amenities...")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT amenity FROM property_amenities ORDER BY amenity")
        amenity_map = {}
        for row in cur.fetchall():
            name = row["amenity"]
            obj, _ = Amenity.objects.get_or_create(name=name)
            amenity_map[name] = obj

        # 3. Import listings
        self.stdout.write("Importing listings...")
        cur.execute("SELECT * FROM properties ORDER BY id")
        properties = cur.fetchall()

        listing_map = {}  # sample property_id → Listing
        for idx, prop in enumerate(properties):
            host = hosts[idx % len(hosts)]
            slug = slugify(f"{prop['name']}-{prop['id']}")
            listing, created = Listing.objects.get_or_create(
                slug=slug,
                defaults={
                    "host": host,
                    "title": prop["name"],
                    "description": prop["description"] or "",
                    "property_type": PROPERTY_TYPE_MAP.get(prop["property_type"], "apartment"),
                    "street_address": prop["address"],
                    "city": prop["city"],
                    "country": prop["country"],
                    "nightly_rate_usd": Decimal(str(prop["base_price_per_night"])),
                    "max_guests": prop["max_guests"],
                    "bedrooms": prop["bedrooms"],
                    "bathrooms": Decimal(str(prop["bathrooms"])),
                    "status": Listing.Status.PUBLISHED,
                    "cancellation_policy": Listing.CancellationPolicy.MODERATE,
                    "location": Point(
                        float(prop["longitude"]),
                        float(prop["latitude"]),
                        srid=4326,
                    ),
                },
            )
            listing_map[prop["id"]] = listing

            if created:
                # Link amenities
                cur2 = conn.cursor()
                cur2.execute(
                    "SELECT amenity FROM property_amenities WHERE property_id = ?",
                    (prop["id"],),
                )
                amenity_names = [r["amenity"] for r in cur2.fetchall()]
                amenity_objs = [amenity_map[n] for n in amenity_names if n in amenity_map]
                if amenity_objs:
                    listing.amenities.set(amenity_objs)

        self.stdout.write(self.style.SUCCESS(f"  {len(listing_map)} listings imported"))

        # 4. Store primary photo CDN URLs
        self.stdout.write("Storing photo URLs...")
        cur.execute("SELECT * FROM property_images WHERE is_primary = 1 ORDER BY property_id")
        photo_count = 0
        for img_row in cur.fetchall():
            listing = listing_map.get(img_row["property_id"])
            if not listing:
                continue
            if listing.photos.exists():
                continue

            ListingPhoto.objects.create(
                listing=listing,
                image_url=img_row["image_url"],
                caption="Primary photo",
                sort_order=0,
            )
            photo_count += 1

        self.stdout.write(self.style.SUCCESS(f"  {photo_count} photo URLs stored"))

        # 5. Import reservations
        self.stdout.write("Importing reservations...")
        cur.execute("SELECT * FROM bookings ORDER BY id")
        bookings = cur.fetchall()

        guest_user_cache = {}
        reservation_count = 0
        sample_reservation = None

        for booking in bookings:
            listing = listing_map.get(booking["property_id"])
            if not listing:
                continue

            email = booking["guest_email"]
            if not email:
                continue

            # Get or create guest user
            if email not in guest_user_cache:
                guest_user_cache[email] = self._create_user(
                    User, email, password="demo12345"
                )
            booking_guest = guest_user_cache[email]

            status = BOOKING_STATUS_MAP.get(booking["status"], "requested")
            created_at = timezone.now()

            reservation, created = Reservation.objects.get_or_create(
                listing=listing,
                guest=booking_guest,
                check_in=booking["check_in"],
                check_out=booking["check_out"],
                defaults={
                    "host": listing.host,
                    "guests": min(listing.max_guests, 2),
                    "total_usd": Decimal(str(booking["total_price"])) if booking["total_price"] else Decimal("0.00"),
                    "status": status,
                    "guest_message": f"Booking by {booking['guest_name'] or 'Guest'}",
                    "expires_at": created_at + timedelta(hours=48),
                },
            )
            if created:
                reservation_count += 1
                if sample_reservation is None and booking_guest.email == "guest@covach.dev":
                    sample_reservation = reservation

        # Assign a few bookings to the designated guest user
        guest_bookings = Reservation.objects.filter(guest=guest).count()
        if guest_bookings == 0 and listing_map:
            # Give the demo guest a couple reservations
            first_listings = list(listing_map.values())[:3]
            for i, lst in enumerate(first_listings):
                Reservation.objects.get_or_create(
                    listing=lst,
                    guest=guest,
                    check_in="2026-03-15",
                    check_out="2026-03-20",
                    defaults={
                        "host": lst.host,
                        "guests": 2,
                        "total_usd": lst.nightly_rate_usd * 5,
                        "status": "approved" if i == 0 else "requested",
                        "guest_message": "Looking forward to the stay!",
                        "expires_at": timezone.now() + timedelta(hours=48),
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"  {reservation_count} reservations imported"))

        # 6. Create availability blocks from pricing_rules
        self.stdout.write("Creating availability blocks...")
        cur.execute("SELECT * FROM pricing_rules ORDER BY id")
        block_count = 0
        for rule in cur.fetchall():
            listing = listing_map.get(rule["property_id"])
            if not listing:
                continue
            _, created = AvailabilityBlock.objects.get_or_create(
                listing=listing,
                start_date=rule["start_date"],
                end_date=rule["end_date"],
                defaults={"reason": "Seasonal pricing"},
            )
            if created:
                block_count += 1

        self.stdout.write(self.style.SUCCESS(f"  {block_count} availability blocks created"))

        # 7. Create sample notifications for guest user
        self.stdout.write("Creating notifications...")
        notifications_data = [
            {
                "notification_type": UserNotification.NotificationType.RESERVATION_APPROVED,
                "title": "Reservation approved!",
                "body": "Your reservation has been approved. Pack your bags!",
            },
            {
                "notification_type": UserNotification.NotificationType.RESERVATION_REQUEST,
                "title": "New reservation request",
                "body": "You have a new reservation request waiting for review.",
            },
            {
                "notification_type": UserNotification.NotificationType.RESERVATION_CANCELED,
                "title": "Reservation canceled",
                "body": "A reservation has been canceled by the host.",
            },
        ]
        notif_count = 0
        for data in notifications_data:
            _, created = UserNotification.objects.get_or_create(
                user=guest,
                title=data["title"],
                defaults={
                    "notification_type": data["notification_type"],
                    "body": data["body"],
                },
            )
            if created:
                notif_count += 1

        self.stdout.write(self.style.SUCCESS(f"  {notif_count} notifications created"))

        conn.close()

        self.stdout.write(self.style.SUCCESS("\nDone! Demo data seeded successfully."))
        self.stdout.write("  Logins:")
        self.stdout.write("    ops@covach.dev / demo12345 (staff)")
        self.stdout.write("    guest@covach.dev / demo12345 (guest)")
        self.stdout.write("    host1@covach.dev .. host5@covach.dev / demo12345 (hosts)")

    def _create_user(self, User, email, is_staff=False, password="demo12345"):
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "is_active": True, "is_staff": is_staff},
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def _flush(self):
        self.stdout.write(self.style.WARNING("Flushing existing demo data..."))
        UserNotification.objects.all().delete()
        AvailabilityBlock.objects.all().delete()
        Reservation.objects.all().delete()
        ListingPhoto.objects.all().delete()
        Listing.objects.all().delete()
        Amenity.objects.all().delete()
        HostProfile.objects.all().delete()
        User = get_user_model()
        User.objects.filter(email__endswith="@covach.dev").delete()
        User.objects.filter(email__endswith="@example.net").delete()
        User.objects.filter(email__endswith="@example.org").delete()
        User.objects.filter(email__endswith="@example.com").delete()
        self.stdout.write(self.style.SUCCESS("  Flushed."))

    def _is_populated(self):
        User = get_user_model()
        return (
            User.objects.exists()
            or Listing.objects.exists()
            or Reservation.objects.exists()
            or HostProfile.objects.exists()
            or Amenity.objects.exists()
            or UserNotification.objects.exists()
        )
