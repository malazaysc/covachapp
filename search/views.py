from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from core.geocode import geocode_city
from listings.models import AvailabilityBlock, Listing
from reservations.models import Reservation
from search.forms import SearchForm


def _search_queryset(cleaned_data):
    queryset = Listing.objects.filter(
        status=Listing.Status.PUBLISHED,
        host__host_profile__status="approved",
    ).prefetch_related("photos")

    if cleaned_data.get("property_type"):
        queryset = queryset.filter(property_type=cleaned_data["property_type"])

    if cleaned_data.get("min_price") is not None:
        queryset = queryset.filter(nightly_rate_usd__gte=cleaned_data["min_price"])

    if cleaned_data.get("max_price") is not None:
        queryset = queryset.filter(nightly_rate_usd__lte=cleaned_data["max_price"])

    if cleaned_data.get("guests"):
        queryset = queryset.filter(max_guests__gte=cleaned_data["guests"])

    location_query = cleaned_data.get("q")
    radius_km = cleaned_data.get("radius_km") or 25
    geocoded = geocode_city(location_query) if location_query else None

    if geocoded:
        center = Point(geocoded["lon"], geocoded["lat"], srid=4326)
        queryset = queryset.filter(location__distance_lte=(center, D(km=radius_km)))

    check_in = cleaned_data.get("check_in")
    check_out = cleaned_data.get("check_out")

    if check_in and check_out and check_in < check_out:
        blocked_listing_ids = AvailabilityBlock.objects.filter(
            start_date__lt=check_out,
            end_date__gt=check_in,
        ).values_list("listing_id", flat=True)
        reserved_listing_ids = Reservation.objects.filter(
            status=Reservation.Status.APPROVED,
            check_in__lt=check_out,
            check_out__gt=check_in,
        ).values_list("listing_id", flat=True)
        queryset = queryset.exclude(Q(id__in=blocked_listing_ids) | Q(id__in=reserved_listing_ids))

    return queryset, geocoded


def home(request):
    form = SearchForm(request.GET or None)
    listings = Listing.objects.filter(status=Listing.Status.PUBLISHED, host__host_profile__status="approved")[:6]
    return render(request, "search/home.html", {"form": form, "listings": listings})


def search_results(request):
    form = SearchForm(request.GET or None)
    listings = Listing.objects.none()
    geocoded = None
    if form.is_valid():
        listings, geocoded = _search_queryset(form.cleaned_data)
    context = {"form": form, "listings": listings, "geocoded": geocoded}
    return render(request, "search/results.html", context)


def htmx_results_partial(request):
    form = SearchForm(request.GET or None)
    listings = Listing.objects.none()
    geocoded = None
    if form.is_valid():
        listings, geocoded = _search_queryset(form.cleaned_data)
    return render(request, "partials/search_results_list.html", {"listings": listings, "geocoded": geocoded})


def htmx_map_payload(request):
    form = SearchForm(request.GET or None)
    listings = Listing.objects.none()
    if form.is_valid():
        listings, _ = _search_queryset(form.cleaned_data)

    payload = []
    for listing in listings:
        if not listing.location:
            continue
        payload.append(
            {
                "id": listing.id,
                "title": listing.title,
                "slug": listing.slug,
                "lat": listing.location.y,
                "lon": listing.location.x,
                "price": str(listing.nightly_rate_usd),
                "city": listing.city,
            }
        )
    return JsonResponse({"results": payload})
