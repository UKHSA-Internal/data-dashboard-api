from django.core.management.base import BaseCommand

from caching.private_api.handlers import force_cache_refresh_for_all_pages


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        force_cache_refresh_for_all_pages()
