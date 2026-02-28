import pytest
from django.urls import reverse

from accounts.models import HostProfile
from tests.factories import UserFactory


@pytest.mark.django_db
def test_unapproved_host_redirected_from_host_listings(client):
    user = UserFactory()
    HostProfile.objects.create(user=user, status=HostProfile.Status.PENDING)
    client.force_login(user)

    response = client.get("/host/listings")
    assert response.status_code == 302
    assert reverse("accounts:apply_host") in response.url


@pytest.mark.django_db
def test_staff_can_access_ops_portal(client):
    admin_user = UserFactory(is_staff=True)
    client.force_login(admin_user)

    response = client.get("/ops/")
    assert response.status_code == 200
