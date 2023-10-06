import uuid

from django.core.management.base import BaseCommand

from metrics.data.managers.api_keys import CustomAPIKeyManager


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--api_key", type=str, required=False)

    def handle(self, *args, **options) -> None:
        """Generates an `APIKey` with the given api key . If not provided, it is auto-generated."""
        kwargs = self._build_kwargs(options=options)
        api_key_model_manager = CustomAPIKeyManager()
        api_key_model_manager.create_key(**kwargs)

    @staticmethod
    def _build_kwargs(options) -> dict[str, str]:
        name = str(uuid.uuid4())
        kwargs = {"name": name}

        if options["api_key"] is not None:
            kwargs["api_key"] = options["api_key"]

        return kwargs
