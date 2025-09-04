from django.core.management.base import BaseCommand

from caching.private_api.handlers import refresh_default_cache


class Command(BaseCommand):
    @classmethod
    def handle(cls, *args, **options) -> None:
        refresh_default_cache()
