from django.core.management.base import BaseCommand

from caching.public_api.handlers import crawl_public_api


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        crawl_public_api()
