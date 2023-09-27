from django.core.management.base import BaseCommand

from caching.public_api.crawler import crawl_public_api_themes_path


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        crawl_public_api_themes_path()
