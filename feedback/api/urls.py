from django.urls import re_path, resolvers

from feedback.api.views import SuggestionsView


def construct_urlpatterns_for_feedback(*, prefix: str) -> list[resolvers.URLResolver]:
    """Builds a list of `URLResolver` instances for the feedback application module

    Args:
        prefix: The prefix to add to the start of the URL paths

    Returns:
        List of `URLResolver` object which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    return [
        re_path(f"^{prefix}suggestions/v1", SuggestionsView.as_view()),
    ]
