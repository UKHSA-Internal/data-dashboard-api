import uuid

from django.core.management.base import BaseCommand

from metrics.data.models.api_keys import CustomAPIKey


class Command(BaseCommand):
    def handle(self, *args, **options) -> str:
        name = str(uuid.uuid4())
        _, key = CustomAPIKey.objects.create_key(name=name, **options)
        return name
