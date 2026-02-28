import datetime
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from accounts.models import HostProfile
from listings.models import Listing
from reservations.models import Reservation


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}@example.com")
    email = factory.LazyAttribute(lambda o: o.username)
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class HostProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HostProfile

    user = factory.SubFactory(UserFactory)
    status = HostProfile.Status.APPROVED


class ListingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Listing

    host = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Listing {n}")
    slug = factory.Sequence(lambda n: f"listing-{n}")
    description = "Great stay"
    property_type = Listing.PropertyType.APARTMENT
    street_address = "123 Main St"
    city = "Austin"
    region = "TX"
    country = "United States"
    nightly_rate_usd = Decimal("120.00")
    max_guests = 4
    bedrooms = 2
    bathrooms = Decimal("1.5")
    status = Listing.Status.PUBLISHED
    cancellation_policy = Listing.CancellationPolicy.MODERATE


class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reservation

    listing = factory.SubFactory(ListingFactory)
    guest = factory.SubFactory(UserFactory)
    host = factory.LazyAttribute(lambda o: o.listing.host)
    check_in = factory.LazyFunction(lambda: datetime.date.today() + datetime.timedelta(days=10))
    check_out = factory.LazyFunction(lambda: datetime.date.today() + datetime.timedelta(days=13))
    guests = 2
    total_usd = Decimal("360.00")
    status = Reservation.Status.REQUESTED
    expires_at = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24))
