from django import forms

from listings.models import Listing

_input = "form-input"
_select = "form-select"


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Location",
        widget=forms.TextInput(attrs={"class": _input, "placeholder": "City or neighborhood"}),
    )
    check_in = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": _input, "type": "date"}),
    )
    check_out = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": _input, "type": "date"}),
    )
    guests = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": _input, "placeholder": "Guests"}),
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": _input, "placeholder": "Min $"}),
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": _input, "placeholder": "Max $"}),
    )
    property_type = forms.ChoiceField(
        required=False,
        choices=[("", "Any type")] + list(Listing.PropertyType.choices),
        widget=forms.Select(attrs={"class": _select}),
    )
    radius_km = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
        initial=25,
        widget=forms.NumberInput(attrs={"class": _input, "placeholder": "Radius km"}),
    )
