from django.core.management.base import BaseCommand
from kaleido import get_chrome_sync


class Command(BaseCommand):
    @classmethod
    def handle(cls, *args, **options):
        get_chrome_sync(verbose=True)
