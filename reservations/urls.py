from django.urls import path

from reservations.views import approve_reservation, cancel_reservation_view, decline_reservation, request_reservation

app_name = "reservations"

urlpatterns = [
    path("request", request_reservation),
    path("request/", request_reservation, name="request"),
    path("<int:pk>/approve", approve_reservation),
    path("<int:pk>/approve/", approve_reservation, name="approve"),
    path("<int:pk>/decline", decline_reservation),
    path("<int:pk>/decline/", decline_reservation, name="decline"),
    path("<int:pk>/cancel", cancel_reservation_view),
    path("<int:pk>/cancel/", cancel_reservation_view, name="cancel"),
]
