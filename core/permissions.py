from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import HostProfile


def approved_host_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = HostProfile.objects.filter(user=request.user).first()
        if not profile or profile.status != HostProfile.Status.APPROVED:
            messages.error(request, "You need an approved host account to access this page.")
            return redirect("accounts:apply_host")
        return view_func(request, *args, **kwargs)

    return _wrapped


def staff_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Admin access required.")
            return redirect("search:home")
        return view_func(request, *args, **kwargs)

    return _wrapped
