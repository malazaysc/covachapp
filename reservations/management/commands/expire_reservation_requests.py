from django.core.management.base import BaseCommand

from reservations.services import expire_open_requests


class Command(BaseCommand):
    help = "Expire stale reservation requests"

    def handle(self, *args, **options):
        count = expire_open_requests()
        self.stdout.write(self.style.SUCCESS(f"Expired {count} reservation requests"))
