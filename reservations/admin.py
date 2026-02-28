from django.contrib import admin

from reservations.models import Reservation, ReservationEvent


class ReservationEventInline(admin.TabularInline):
    model = ReservationEvent
    extra = 0


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("listing", "guest", "host", "status", "check_in", "check_out", "total_usd")
    list_filter = ("status",)
    inlines = [ReservationEventInline]


admin.site.register(ReservationEvent)
