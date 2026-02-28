from django.contrib import admin

from listings.models import Amenity, AvailabilityBlock, Listing, ListingPhoto


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "host", "status", "city", "nightly_rate_usd", "updated_at")
    list_filter = ("status", "property_type", "cancellation_policy")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingPhotoInline]


admin.site.register(Amenity)
admin.site.register(AvailabilityBlock)
admin.site.register(ListingPhoto)
