from django.contrib import admin

from accounts.models import EmailVerificationToken, HostProfile


@admin.register(HostProfile)
class HostProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "updated_at")
    list_filter = ("status",)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "used_at")
