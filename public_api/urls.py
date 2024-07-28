from django.urls import include, path, resolvers

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


def construct_versioned_urlpatterns_for_public_api(
    *,
    prefix: str,
) -> list[resolvers.URLResolver]:
    """Returns a version set of URLResolvers for `public_api endpoints

    Args:
        prefix: The prefix to add to the start of the url paths

    Returns
        List of `URLResolver` objects each representing a
        set of versioned URLS which can then be consumed by
        the django application via `urlpatterns` in `urls.py`

    """
    return [
        path(prefix, include(_construct_urlpatterns_for_public_api(), namespace="v1")),
        path(
            f"{prefix}/v2",
            include(_construct_urlpatterns_for_public_api(), namespace="v2"),
        ),
    ]


def _construct_urlpatterns_for_public_api() -> list[resolvers.URLResolver]:
    """Builds a list of `URLResolver` instances for the public API application module

    Returns:
        List of `URLResolver` object which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    return (
        [
            path("", PublicAPIRootView.as_view(), name="public-api-root"),
            path("themes/", ThemeListView.as_view(), name="theme-list"),
            path(
                "themes/<str:theme>",
                ThemeDetailView.as_view(),
                name="theme-detail",
            ),
            path(
                "themes/<str:theme>/sub_themes/",
                SubThemeListView.as_view(),
                name="sub_theme-list",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>",
                SubThemeDetailView.as_view(),
                name="sub_theme-detail",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
                TopicListView.as_view(),
                name="topic-list",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>",
                TopicDetailView.as_view(),
                name="topic-detail",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types",
                GeographyTypeListView.as_view(),
                name="geography_type-list",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>",
                GeographyTypeDetailView.as_view(),
                name="geography_type-detail",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies",
                GeographyListView.as_view(),
                name="geography-list",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>",
                GeographyDetailView.as_view(),
                name="geography-detail",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics",
                MetricListView.as_view(),
                name="metric-list",
            ),
            path(
                "themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics/<str:metric>",
                APITimeSeriesViewSet.as_view(
                    {"get": "list"}, name=APITimeSeriesViewSet.name
                ),
                name="timeseries-list",
            ),
        ],
        "public_api",
    )
