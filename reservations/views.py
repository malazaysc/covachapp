from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from listings.models import Listing
from reservations.forms import ReservationRequestForm
from reservations.services import ReservationError, approve_request, cancel_reservation, create_request, decline_request


@login_required
def request_reservation(request):
    if request.method != "POST":
        messages.error(request, "Invalid reservation request.")
        return redirect("search:home")

    form = ReservationRequestForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct booking details.")
        return redirect(request.META.get("HTTP_REFERER", "search:home"))

    listing = get_object_or_404(Listing, pk=form.cleaned_data["listing_id"])

    try:
        create_request(
            guest=request.user,
            listing=listing,
            check_in=form.cleaned_data["check_in"],
            check_out=form.cleaned_data["check_out"],
            guests=form.cleaned_data["guests"],
            message=form.cleaned_data.get("guest_message", ""),
        )
        messages.success(request, "Reservation request sent to host.")
    except ReservationError as exc:
        messages.error(request, str(exc))

    return redirect("listings:detail", slug=listing.slug)


@login_required
def approve_reservation(request, pk):
    if request.method != "POST":
        return redirect("accounts:host_reservations")
    try:
        approve_request(reservation_id=pk, actor=request.user)
        messages.success(request, "Reservation approved.")
    except ReservationError as exc:
        messages.error(request, str(exc))
    return redirect("accounts:host_reservations")


@login_required
def decline_reservation(request, pk):
    if request.method != "POST":
        return redirect("accounts:host_reservations")
    try:
        decline_request(reservation_id=pk, actor=request.user)
        messages.success(request, "Reservation declined.")
    except ReservationError as exc:
        messages.error(request, str(exc))
    return redirect("accounts:host_reservations")


@login_required
def cancel_reservation_view(request, pk):
    if request.method != "POST":
        return redirect("accounts:guest_trips")
    try:
        reservation = cancel_reservation(reservation_id=pk, actor=request.user)
        messages.success(
            request,
            f"Reservation canceled. Cancellation fee: ${reservation.cancellation_fee_usd}",
        )
    except ReservationError as exc:
        messages.error(request, str(exc))
    return redirect(request.META.get("HTTP_REFERER", "/"))
