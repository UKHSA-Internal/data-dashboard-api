import uuid

from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        _, key = APIKey.objects.create_key(name=str(uuid.uuid4()))
        return key
