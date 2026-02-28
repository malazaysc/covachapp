from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from accounts.models import EmailVerificationToken


def send_verification_email(user, request):
    token = EmailVerificationToken.create_for_user(user)
    verify_link = request.build_absolute_uri(reverse("accounts:verify_email", args=[str(token.token)]))

    send_mail(
        subject="Verify your Covach account",
        message=f"Welcome to Covach. Verify your email: {verify_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
