from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

_input = "form-input"
_textarea = "form-textarea"


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": _input, "placeholder": "you@example.com"}),
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": _input, "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": _input, "placeholder": "Last name"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": _input, "placeholder": "Create a password"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": _input, "placeholder": "Confirm your password"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower().strip()
        user.email = self.cleaned_data["email"].lower().strip()
        user.is_active = False
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": _input, "placeholder": "you@example.com"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": _input, "placeholder": "Your password"}),
    )

    def clean(self):
        cleaned = super().clean()
        self.cleaned_data["username"] = self.cleaned_data.get("username", "").lower().strip()
        return cleaned
