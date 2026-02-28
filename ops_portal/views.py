from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import HostProfile
from core.permissions import staff_required
from listings.models import Listing
from notifications.models import UserNotification
from notifications.services import notify_user
from reservations.models import Reservation


@staff_required
def ops_home(request):
    metrics = {
        "hosts_pending": HostProfile.objects.filter(status=HostProfile.Status.PENDING).count(),
        "listings_published": Listing.objects.filter(status=Listing.Status.PUBLISHED).count(),
        "reservation_requests": Reservation.objects.filter(status=Reservation.Status.REQUESTED).count(),
    }
    return render(request, "ops_portal/home.html", {"metrics": metrics})


@staff_required
def ops_hosts(request):
    hosts = HostProfile.objects.select_related("user").all()
    return render(request, "ops_portal/hosts.html", {"hosts": hosts})


@staff_required
def approve_host(request, pk):
    if request.method == "POST":
        host = get_object_or_404(HostProfile, pk=pk)
        host.status = HostProfile.Status.APPROVED
        host.save(update_fields=["status", "updated_at"])
        notify_user(
            host.user,
            UserNotification.NotificationType.HOST_STATUS,
            "Host application approved",
            "Your host application has been approved. You can now publish listings.",
            payload={"host_profile_id": host.id, "status": host.status},
        )
        messages.success(request, f"Approved host {host.user.email}.")
    return redirect("ops_portal:hosts")


@staff_required
def reject_host(request, pk):
    if request.method == "POST":
        host = get_object_or_404(HostProfile, pk=pk)
        host.status = HostProfile.Status.REJECTED
        host.save(update_fields=["status", "updated_at"])
        notify_user(
            host.user,
            UserNotification.NotificationType.HOST_STATUS,
            "Host application update",
            "Your host application was not approved. Contact support for details.",
            payload={"host_profile_id": host.id, "status": host.status},
        )
        messages.success(request, f"Rejected host {host.user.email}.")
    return redirect("ops_portal:hosts")


@staff_required
def ops_listings(request):
    listings = Listing.objects.select_related("host").all()
    return render(request, "ops_portal/listings.html", {"listings": listings})


@staff_required
def ops_reservations(request):
    reservations = Reservation.objects.select_related("listing", "guest", "host").all()
    return render(request, "ops_portal/reservations.html", {"reservations": reservations})


@staff_required
def ops_metrics(request):
    revenue = Reservation.objects.filter(status=Reservation.Status.APPROVED).aggregate(total=Sum("total_usd"))["total"]
    by_status = Reservation.objects.values("status").annotate(total=Count("id")).order_by("status")
    return render(
        request,
        "ops_portal/metrics.html",
        {
            "revenue": revenue or 0,
            "by_status": by_status,
        },
    )
