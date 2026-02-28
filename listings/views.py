from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import approved_host_required
from listings.forms import AvailabilityBlockForm, ListingForm, ListingPhotoForm
from listings.models import AvailabilityBlock, Listing, ListingPhoto
from reservations.models import Reservation


def listing_detail(request, slug):
    listing = get_object_or_404(Listing.objects.prefetch_related("photos", "amenities"), slug=slug)
    return render(request, "listings/detail.html", {"listing": listing})


@approved_host_required
def host_listings(request):
    listings = Listing.objects.filter(host=request.user).prefetch_related("amenities")
    return render(request, "listings/host_listings.html", {"listings": listings})


@approved_host_required
def listing_create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.host = request.user
            listing.save()
            form.save_m2m()
            messages.success(request, "Listing created.")
            return redirect("listings:edit", pk=listing.pk)
    else:
        form = ListingForm()
    return render(request, "listings/form.html", {"form": form, "mode": "create"})


@approved_host_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, host=request.user)
    initial = {}
    if listing.location:
        initial = {"latitude": listing.location.y, "longitude": listing.location.x}

    form = ListingForm(instance=listing, initial=initial)
    block_form = AvailabilityBlockForm()
    photo_form = ListingPhotoForm()

    if request.method == "POST" and request.POST.get("block_form") == "1":
        block_form = AvailabilityBlockForm(request.POST)
        if block_form.is_valid():
            block = block_form.save(commit=False)
            block.listing = listing
            block.save()
            messages.success(request, "Availability block added.")
            return redirect("listings:edit", pk=listing.pk)
    elif request.method == "POST" and request.POST.get("photo_form") == "1":
        photo_form = ListingPhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.listing = listing
            photo.save()
            messages.success(request, "Photo added.")
            return redirect("listings:edit", pk=listing.pk)
    elif request.method == "POST":
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated.")
            return redirect("listings:edit", pk=listing.pk)

    photos = ListingPhoto.objects.filter(listing=listing)
    blocks = listing.availability_blocks.all()

    return render(
        request,
        "listings/form.html",
        {
            "form": form,
            "listing": listing,
            "mode": "edit",
            "block_form": block_form,
            "photo_form": photo_form,
            "blocks": blocks,
            "photos": photos,
        },
    )


@login_required
def listing_availability_partial(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    approved_reservations = Reservation.objects.filter(
        listing=listing,
        status=Reservation.Status.APPROVED,
    ).values("check_in", "check_out")
    blocks = AvailabilityBlock.objects.filter(listing=listing).values("start_date", "end_date", "reason")
    return render(
        request,
        "partials/availability_table.html",
        {
            "listing": listing,
            "approved_reservations": approved_reservations,
            "blocks": blocks,
        },
    )


@approved_host_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, host=request.user)
    if request.method == "POST":
        listing.status = Listing.Status.ARCHIVED
        listing.save(update_fields=["status", "updated_at"])
        messages.success(request, "Listing archived.")
        return redirect("listings:host_listings")
    return render(request, "listings/delete_confirm.html", {"listing": listing})


def published_listings_queryset():
    return Listing.objects.filter(status=Listing.Status.PUBLISHED).filter(
        Q(host__host_profile__status="approved")
    )
