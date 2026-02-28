from django import forms
from django.contrib.gis.geos import Point

from listings.models import AvailabilityBlock, Listing, ListingPhoto

_input = "form-input"
_select = "form-select"
_textarea = "form-textarea"


class ListingForm(forms.ModelForm):
    latitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": _input, "placeholder": "e.g. 37.7739", "step": "any"}),
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": _input, "placeholder": "e.g. -122.4312", "step": "any"}),
    )

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "property_type",
            "street_address",
            "city",
            "region",
            "country",
            "postal_code",
            "nightly_rate_usd",
            "max_guests",
            "bedrooms",
            "bathrooms",
            "status",
            "cancellation_policy",
            "amenities",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": _input, "placeholder": "Give your listing a name"}),
            "description": forms.Textarea(attrs={"class": _textarea, "rows": 4, "placeholder": "Describe your space..."}),
            "property_type": forms.Select(attrs={"class": _select}),
            "street_address": forms.TextInput(attrs={"class": _input, "placeholder": "123 Main St"}),
            "city": forms.TextInput(attrs={"class": _input, "placeholder": "City"}),
            "region": forms.TextInput(attrs={"class": _input, "placeholder": "State / Region"}),
            "country": forms.TextInput(attrs={"class": _input, "placeholder": "Country"}),
            "postal_code": forms.TextInput(attrs={"class": _input, "placeholder": "Postal code"}),
            "nightly_rate_usd": forms.NumberInput(attrs={"class": _input, "placeholder": "0.00", "step": "0.01"}),
            "max_guests": forms.NumberInput(attrs={"class": _input, "min": "1"}),
            "bedrooms": forms.NumberInput(attrs={"class": _input, "min": "0"}),
            "bathrooms": forms.NumberInput(attrs={"class": _input, "min": "0"}),
            "status": forms.Select(attrs={"class": _select}),
            "cancellation_policy": forms.Select(attrs={"class": _select}),
            "amenities": forms.CheckboxSelectMultiple(attrs={"class": ""}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        lat = self.cleaned_data.get("latitude")
        lon = self.cleaned_data.get("longitude")
        if lat is not None and lon is not None:
            instance.location = Point(lon, lat, srid=4326)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class AvailabilityBlockForm(forms.ModelForm):
    class Meta:
        model = AvailabilityBlock
        fields = ["start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"class": _input, "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": _input, "type": "date"}),
            "reason": forms.TextInput(attrs={"class": _input, "placeholder": "Optional reason"}),
        }


class ListingPhotoForm(forms.ModelForm):
    class Meta:
        model = ListingPhoto
        fields = ["image", "caption", "sort_order"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": _input}),
            "caption": forms.TextInput(attrs={"class": _input, "placeholder": "Photo caption"}),
            "sort_order": forms.NumberInput(attrs={"class": _input, "min": "0"}),
        }
