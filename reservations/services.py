from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from accounts.models import HostProfile
from listings.models import AvailabilityBlock, Listing
from notifications.models import UserNotification
from notifications.services import notify_user
from reservations.models import Reservation, ReservationEvent


class ReservationError(Exception):
    pass


def calculate_total_usd(listing: Listing, check_in, check_out) -> Decimal:
    nights = (check_out - check_in).days
    return listing.nightly_rate_usd * nights


def _overlaps(listing, check_in, check_out):
    return Reservation.objects.filter(
        listing=listing,
        status=Reservation.Status.APPROVED,
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()


def _blocked(listing, check_in, check_out):
    return AvailabilityBlock.objects.filter(
        listing=listing,
        start_date__lt=check_out,
        end_date__gt=check_in,
    ).exists()


def create_request(*, guest, listing: Listing, check_in, check_out, guests, message=""):
    if check_in >= check_out:
        raise ReservationError("Check-out date must be after check-in date.")
    if listing.status != Listing.Status.PUBLISHED:
        raise ReservationError("This listing is not available for booking.")
    if not hasattr(listing.host, "host_profile") or listing.host.host_profile.status != HostProfile.Status.APPROVED:
        raise ReservationError("Host is not approved for reservations.")
    if guest == listing.host:
        raise ReservationError("Hosts cannot reserve their own listings.")
    if guests > listing.max_guests:
        raise ReservationError("Guest count exceeds listing capacity.")
    if _blocked(listing, check_in, check_out):
        raise ReservationError("Selected dates are blocked by the host.")
    if _overlaps(listing, check_in, check_out):
        raise ReservationError("Selected dates are already reserved.")

    ttl_hours = getattr(settings, "COVACH_RESERVATION_REQUEST_TTL_HOURS", 24)
    reservation = Reservation.objects.create(
        listing=listing,
        guest=guest,
        host=listing.host,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        total_usd=calculate_total_usd(listing, check_in, check_out),
        guest_message=message,
        expires_at=timezone.now() + timezone.timedelta(hours=ttl_hours),
        status=Reservation.Status.REQUESTED,
    )
    ReservationEvent.objects.create(
        reservation=reservation,
        actor=guest,
        event_type="request_created",
        message="Reservation request submitted",
    )
    notify_user(
        listing.host,
        UserNotification.NotificationType.RESERVATION_REQUEST,
        "New reservation request",
        f"{guest.get_full_name() or guest.email} requested {listing.title} from {check_in} to {check_out}.",
        payload={"reservation_id": reservation.id},
    )
    return reservation


def _calculate_cancellation_fee(reservation: Reservation, canceled_at):
    days_before = (reservation.check_in - canceled_at.date()).days
    policy = reservation.listing.cancellation_policy

    if policy == Listing.CancellationPolicy.FLEXIBLE:
        pct = Decimal("0.00") if days_before >= 1 else Decimal("0.50")
    elif policy == Listing.CancellationPolicy.MODERATE:
        pct = Decimal("0.00") if days_before >= 5 else Decimal("0.50")
    else:
        pct = Decimal("0.00") if days_before >= 7 else Decimal("1.00")
    return (reservation.total_usd * pct).quantize(Decimal("0.01"))


def approve_request(*, reservation_id, actor):
    with transaction.atomic():
        reservation = Reservation.objects.select_for_update().select_related("listing", "guest", "host").get(pk=reservation_id)
        if reservation.host_id != actor.id:
            raise ReservationError("Only the host can approve this request.")
        if reservation.status != Reservation.Status.REQUESTED:
            raise ReservationError("Only requested reservations can be approved.")
        if reservation.expires_at <= timezone.now():
            reservation.status = Reservation.Status.EXPIRED
            reservation.save(update_fields=["status", "updated_at"])
            raise ReservationError("Reservation request has expired.")
        if _overlaps(reservation.listing, reservation.check_in, reservation.check_out):
            raise ReservationError("Another approved reservation overlaps these dates.")

        reservation.status = Reservation.Status.APPROVED
        reservation.save(update_fields=["status", "updated_at"])
        ReservationEvent.objects.create(
            reservation=reservation,
            actor=actor,
            event_type="request_approved",
            message="Host approved reservation",
        )

    notify_user(
        reservation.guest,
        UserNotification.NotificationType.RESERVATION_APPROVED,
        "Reservation approved",
        f"Your reservation for {reservation.listing.title} was approved.",
        payload={"reservation_id": reservation.id},
    )
    return reservation


def decline_request(*, reservation_id, actor):
    with transaction.atomic():
        reservation = Reservation.objects.select_for_update().select_related("listing", "guest", "host").get(pk=reservation_id)
        if reservation.host_id != actor.id:
            raise ReservationError("Only the host can decline this request.")
        if reservation.status != Reservation.Status.REQUESTED:
            raise ReservationError("Only requested reservations can be declined.")
        reservation.status = Reservation.Status.DECLINED
        reservation.save(update_fields=["status", "updated_at"])
        ReservationEvent.objects.create(
            reservation=reservation,
            actor=actor,
            event_type="request_declined",
            message="Host declined reservation",
        )

    notify_user(
        reservation.guest,
        UserNotification.NotificationType.RESERVATION_DECLINED,
        "Reservation declined",
        f"Your reservation request for {reservation.listing.title} was declined.",
        payload={"reservation_id": reservation.id},
    )
    return reservation


def cancel_reservation(*, reservation_id, actor):
    with transaction.atomic():
        reservation = Reservation.objects.select_for_update().select_related("listing", "guest", "host").get(pk=reservation_id)
        if actor.id not in {reservation.guest_id, reservation.host_id}:
            raise ReservationError("Only reservation participants can cancel.")
        if reservation.status not in {Reservation.Status.REQUESTED, Reservation.Status.APPROVED}:
            raise ReservationError("Reservation cannot be canceled in this state.")

        canceled_at = timezone.now()
        reservation.status = Reservation.Status.CANCELED
        reservation.cancellation_fee_usd = _calculate_cancellation_fee(reservation, canceled_at)
        reservation.save(update_fields=["status", "cancellation_fee_usd", "updated_at"])
        ReservationEvent.objects.create(
            reservation=reservation,
            actor=actor,
            event_type="reservation_canceled",
            message="Reservation canceled",
            metadata={"fee_usd": str(reservation.cancellation_fee_usd)},
        )

    other_party = reservation.host if actor.id == reservation.guest_id else reservation.guest
    notify_user(
        other_party,
        UserNotification.NotificationType.RESERVATION_CANCELED,
        "Reservation canceled",
        f"Reservation for {reservation.listing.title} was canceled."
        f" Cancellation fee: ${reservation.cancellation_fee_usd}.",
        payload={"reservation_id": reservation.id, "fee_usd": str(reservation.cancellation_fee_usd)},
    )
    return reservation


def expire_open_requests():
    expired = Reservation.objects.filter(
        status=Reservation.Status.REQUESTED,
        expires_at__lte=timezone.now(),
    ).select_related("listing", "guest")

    count = 0
    for reservation in expired:
        reservation.status = Reservation.Status.EXPIRED
        reservation.save(update_fields=["status", "updated_at"])
        ReservationEvent.objects.create(
            reservation=reservation,
            actor=None,
            event_type="request_expired",
            message="Request expired",
        )
        notify_user(
            reservation.guest,
            UserNotification.NotificationType.RESERVATION_EXPIRED,
            "Reservation request expired",
            f"Your reservation request for {reservation.listing.title} has expired.",
            payload={"reservation_id": reservation.id},
        )
        count += 1
    return count
