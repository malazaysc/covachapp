from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.forms import SignUpForm, StyledAuthenticationForm
from accounts.models import EmailVerificationToken, HostProfile
from accounts.services import send_verification_email
from notifications.models import UserNotification
from reservations.models import Reservation


class AccountLoginView(LoginView):
    form_class = StyledAuthenticationForm
    template_name = "accounts/login.html"


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(user, request)
            messages.success(request, "Account created. Check your email to verify your account.")
            return redirect("accounts:login")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def verify_email_view(request, token):
    email_token = get_object_or_404(EmailVerificationToken, token=token)
    if not email_token.is_valid:
        messages.error(request, "Verification link expired or already used.")
        return redirect("accounts:login")

    email_token.used_at = timezone.now()
    email_token.save(update_fields=["used_at"])
    user = email_token.user
    user.is_active = True
    user.save(update_fields=["is_active"])

    messages.success(request, "Email verified. You can now log in.")
    return redirect("accounts:login")


@login_required
def apply_host_view(request):
    profile, _ = HostProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.bio = request.POST.get("bio", "").strip()
        profile.status = HostProfile.Status.PENDING
        profile.save(update_fields=["bio", "status", "updated_at"])
        messages.success(request, "Host application submitted for review.")
        return redirect("accounts:host_dashboard")
    return render(request, "accounts/apply_host.html", {"profile": profile})


@login_required
def host_dashboard(request):
    profile = HostProfile.objects.filter(user=request.user).first()
    listings = request.user.hosted_listings.all() if profile else []
    pending_reservations = Reservation.objects.filter(
        host=request.user,
        status=Reservation.Status.REQUESTED,
    ).select_related("listing", "guest")
    return render(
        request,
        "accounts/host_dashboard.html",
        {
            "profile": profile,
            "listings": listings,
            "pending_reservations": pending_reservations[:5],
        },
    )


@login_required
def host_reservations(request):
    reservations = Reservation.objects.filter(host=request.user).select_related("listing", "guest")
    return render(request, "accounts/host_reservations.html", {"reservations": reservations})


@login_required
def guest_trips(request):
    reservations = Reservation.objects.filter(guest=request.user).select_related("listing", "host")
    return render(request, "accounts/guest_trips.html", {"reservations": reservations})


@login_required
def guest_inbox(request):
    notifications = UserNotification.objects.filter(user=request.user)
    return render(request, "accounts/guest_inbox.html", {"notifications": notifications})


@login_required
def resend_verification(request):
    User = get_user_model()
    user = User.objects.get(pk=request.user.pk)
    if user.is_active:
        messages.info(request, "Your email is already verified.")
    else:
        send_verification_email(user, request)
        messages.success(request, "Verification email resent.")
    return redirect("search:home")
