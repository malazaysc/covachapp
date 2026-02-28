import datetime

import pytest

from accounts.models import HostProfile
from notifications.models import UserNotification
from reservations.models import Reservation
from reservations.services import ReservationError, approve_request, create_request
from tests.factories import HostProfileFactory, ListingFactory, ReservationFactory, UserFactory


@pytest.mark.django_db
def test_create_request_sends_host_notification(settings):
    guest = UserFactory()
    host_profile = HostProfileFactory()
    listing = ListingFactory(host=host_profile.user)

    reservation = create_request(
        guest=guest,
        listing=listing,
        check_in=datetime.date.today() + datetime.timedelta(days=10),
        check_out=datetime.date.today() + datetime.timedelta(days=13),
        guests=2,
    )

    assert reservation.status == Reservation.Status.REQUESTED
    assert UserNotification.objects.filter(
        user=listing.host,
        notification_type=UserNotification.NotificationType.RESERVATION_REQUEST,
    ).exists()


@pytest.mark.django_db
def test_approve_request_rejects_overlap():
    host_profile = HostProfileFactory(status=HostProfile.Status.APPROVED)
    listing = ListingFactory(host=host_profile.user)
    existing = ReservationFactory(
        listing=listing,
        host=listing.host,
        status=Reservation.Status.APPROVED,
        check_in=datetime.date.today() + datetime.timedelta(days=8),
        check_out=datetime.date.today() + datetime.timedelta(days=12),
    )
    pending = ReservationFactory(
        listing=listing,
        host=listing.host,
        status=Reservation.Status.REQUESTED,
        check_in=datetime.date.today() + datetime.timedelta(days=10),
        check_out=datetime.date.today() + datetime.timedelta(days=13),
    )

    with pytest.raises(ReservationError):
        approve_request(reservation_id=pending.id, actor=listing.host)

    existing.refresh_from_db()
    pending.refresh_from_db()
    assert existing.status == Reservation.Status.APPROVED
    assert pending.status == Reservation.Status.REQUESTED
