from django.urls import re_path, resolvers

from ingestion.api.views.ingestion import IngestionView


def construct_urlpatterns_for_ingestion(prefix: str) -> list[resolvers.URLResolver]:
    """Builds a list of `URLResolver` instances for the ingestion application module

    Args:
        prefix: The prefix to add to the start of the URL paths

    Returns:
        List of `URLResolver` object which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    return [
        re_path(f"^{prefix}ingestion/v1", IngestionView.as_view()),
    ]
