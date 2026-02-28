from django.urls import path

from listings.views import (
    host_listings,
    listing_availability_partial,
    listing_create,
    listing_delete,
    listing_detail,
    listing_edit,
)

app_name = "listings"

urlpatterns = [
    path("<slug:slug>", listing_detail),
    path("<slug:slug>/", listing_detail, name="detail"),
    path("host/listings/", host_listings, name="host_listings"),
    path("host/listings/new/", listing_create, name="create"),
    path("host/listings/<int:pk>/edit/", listing_edit, name="edit"),
    path("host/listings/<int:pk>/archive/", listing_delete, name="archive"),
    path("hx/listings/<int:pk>/availability", listing_availability_partial),
    path("hx/listings/<int:pk>/availability/", listing_availability_partial, name="availability"),
]
