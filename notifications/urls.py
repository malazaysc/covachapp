from django.urls import path

from notifications.views import inbox_partial, mark_read_partial

app_name = "notifications"

urlpatterns = [
    path("hx/inbox/", inbox_partial, name="inbox_partial"),
    path("hx/inbox/<int:pk>/read/", mark_read_partial, name="mark_read"),
]
