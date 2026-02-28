from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts.views import (
    AccountLoginView,
    apply_host_view,
    guest_inbox,
    guest_trips,
    host_dashboard,
    host_reservations,
    resend_verification,
    signup_view,
    verify_email_view,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/<uuid:token>/", verify_email_view, name="verify_email"),
    path("resend-verification/", resend_verification, name="resend_verification"),
    path("host/apply/", apply_host_view, name="apply_host"),
    path("host/dashboard/", host_dashboard, name="host_dashboard"),
    path("host/reservations/", host_reservations, name="host_reservations"),
    path("guest/trips/", guest_trips, name="guest_trips"),
    path("guest/inbox/", guest_inbox, name="guest_inbox"),
]
