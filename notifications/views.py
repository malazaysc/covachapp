from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from notifications.models import UserNotification


@login_required
def inbox_partial(request):
    notifications = UserNotification.objects.filter(user=request.user)
    return render(request, "partials/inbox_list.html", {"notifications": notifications})


@login_required
def mark_read_partial(request, pk):
    if request.method != "POST":
        return inbox_partial(request)
    note = get_object_or_404(UserNotification, pk=pk, user=request.user)
    note.read_at = timezone.now()
    note.save(update_fields=["read_at"])
    notifications = UserNotification.objects.filter(user=request.user)
    return render(request, "partials/inbox_list.html", {"notifications": notifications})
