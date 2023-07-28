from django.urls import path, resolvers

from public_api.views import (
    GeographyDetailView,
    GeographyListView,
    GeographyTypeDetailView,
    GeographyTypeListView,
    MetricListView,
    PublicAPIRootView,
    SubThemeDetailView,
    SubThemeListView,
    ThemeDetailView,
    ThemeListView,
    TopicDetailView,
    TopicListView,
)
from public_api.views.timeseries_viewset import APITimeSeriesViewSet


def construct_urlpatterns_for_public_api(
    prefix: str,
) -> list[resolvers.URLResolver]:
    """Builds a list of `URLResolver` instances for the public API application module

    Args:
        prefix: The prefix to add to the start of the URL paths

    Returns:
        List of `URLResolver` object which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    return [
        path(prefix, PublicAPIRootView.as_view(), name="public-api-root"),
        path(f"{prefix}themes/", ThemeListView.as_view(), name="theme-list"),
        path(
            f"{prefix}themes/<str:theme>",
            ThemeDetailView.as_view(),
            name="theme-detail",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/",
            SubThemeListView.as_view(),
            name="sub_theme-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>",
            SubThemeDetailView.as_view(),
            name="sub_theme-detail",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
            TopicListView.as_view(),
            name="topic-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>",
            TopicDetailView.as_view(),
            name="topic-detail",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types",
            GeographyTypeListView.as_view(),
            name="geography_type-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>",
            GeographyTypeDetailView.as_view(),
            name="geography_type-detail",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies",
            GeographyListView.as_view(),
            name="geography-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>",
            GeographyDetailView.as_view(),
            name="geography-detail",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics",
            MetricListView.as_view(),
            name="metric-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics/<str:metric>",
            APITimeSeriesViewSet.as_view(
                {"get": "list"}, name=APITimeSeriesViewSet.name
            ),
            name="timeseries-list",
        ),
    ]
