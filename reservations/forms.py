from django import forms

_input = "form-input"
_textarea = "form-textarea"


class ReservationRequestForm(forms.Form):
    listing_id = forms.IntegerField(widget=forms.HiddenInput)
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={"class": _input, "type": "date"}),
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={"class": _input, "type": "date"}),
    )
    guests = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": _input}),
    )
    guest_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": _textarea, "rows": 3, "placeholder": "Introduce yourself to the host..."}),
    )
