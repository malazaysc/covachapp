from django.contrib import admin

from notifications.models import UserNotification


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "title", "read_at", "created_at")
    list_filter = ("notification_type",)
