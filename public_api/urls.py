from django.urls import path, resolvers

from public_api.views import (
    GeographyListView,
    GeographyTypeListView,
    MetricListView,
    PublicAPIRootView,
    SubThemeListView,
    ThemeListView,
    TopicListView,
)
from public_api.views.timeseries_viewset import APITimeSeriesViewSet


def construct_url_patterns_for_public_api(
    *,
    prefix: str,
) -> list[resolvers.URLResolver]:
    """Returns a set of URLResolvers for `public_api` endpoints

    Args:
        prefix: The prefix to add to the start of the paths

    Returns:
        List of `URLResolver` objects each representing a
        set of versioned URLS.
    """
    urls = []
    urls.extend(_construct_version_three_urls(prefix=prefix))

    return urls


def _construct_version_three_urls(
    *,
    prefix: str,
) -> list[resolvers.URLResolver]:
    """Returns a list of URLResolvers for the public_api version 1

    Args:
        prefix: The prefix to add to the start of the url paths

    Returns:
        List of `URLResolver` objects each representing a
        set of versioned URLS.
    """
    return [
        path(prefix, PublicAPIRootView.as_view(), name="public-api-root-version-3"),
        path(f"{prefix}themes/", ThemeListView.as_view(), name="theme-list"),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/",
            SubThemeListView.as_view(),
            name="sub_theme-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
            TopicListView.as_view(),
            name="topic-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types",
            GeographyTypeListView.as_view(),
            name="geography_type-list",
        ),
        path(
            f"{prefix}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies",
            GeographyListView.as_view(),
            name="geography-list",
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
