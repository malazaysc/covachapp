import datetime

import pytest

from listings.models import AvailabilityBlock
from reservations.models import Reservation
from tests.factories import HostProfileFactory, ListingFactory, ReservationFactory


@pytest.mark.django_db
def test_search_excludes_blocked_and_reserved(client):
    host = HostProfileFactory().user
    open_listing = ListingFactory(host=host, slug="open-stay")
    blocked_listing = ListingFactory(host=host, slug="blocked-stay")
    reserved_listing = ListingFactory(host=host, slug="reserved-stay")

    check_in = datetime.date.today() + datetime.timedelta(days=20)
    check_out = datetime.date.today() + datetime.timedelta(days=23)

    AvailabilityBlock.objects.create(
        listing=blocked_listing,
        start_date=check_in,
        end_date=check_out,
        reason="Owner visit",
    )

    ReservationFactory(
        listing=reserved_listing,
        host=host,
        status=Reservation.Status.APPROVED,
        check_in=check_in,
        check_out=check_out,
    )

    response = client.get(
        "/search/",
        {
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
        },
    )

    content = response.content.decode()
    assert open_listing.title in content
    assert blocked_listing.title not in content
    assert reserved_listing.title not in content
