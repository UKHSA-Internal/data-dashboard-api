import uuid

from django.core.management.base import BaseCommand

from metrics.data.models.api_keys import CustomAPIKey


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--password_prefix", type=str, required=False)
        parser.add_argument("--password_suffix", type=str, required=False)

    def handle(self, *args, **options) -> None:
        """Generates an `APIKey` with the given password components. If not provided, it is auto-generated."""
        kwargs = self._build_kwargs(options=options)
        CustomAPIKey.objects.create_key(**kwargs)

    @staticmethod
    def _build_kwargs(options):
        name = str(uuid.uuid4())
        kwargs = {"name": name}

        if options["password_prefix"] is not None:
            kwargs["password_prefix"] = options["password_prefix"]

        if options["password_suffix"] is not None:
            kwargs["password_suffix"] = options["password_suffix"]

        return kwargs
