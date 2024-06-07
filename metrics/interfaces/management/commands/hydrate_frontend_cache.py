from django.core.management.base import BaseCommand

from caching.frontend.handlers import crawl_front_end


class Command(BaseCommand):
    @classmethod
    def handle(cls, *args, **options) -> None:
        crawl_front_end()
