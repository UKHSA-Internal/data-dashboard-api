from django.urls import path, resolvers
from django.views.generic import TemplateView

from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.version_02.views import (
    GeographyDetailViewV2,
    GeographyListViewV2,
    GeographyTypeDetailViewV2,
    GeographyTypeListViewV2,
    MetricListViewV2,
    PublicAPIRootViewV2,
    SubThemeDetailViewV2,
    SubThemeListViewV2,
    ThemeDetailViewV2,
    ThemeListViewV2,
    TopicDetailViewV2,
    TopicListViewV2,
)
from public_api.version_02.views.timeseries_viewset import (
    APITimeSeriesViewSetV2,
    APITimeSeriesViewSetV3,
)
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
    urls.extend(_construct_version_one_urls(prefix=prefix))
    urls.extend(_construct_version_two_urls(prefix=prefix))
    urls.extend(_construct_version_three_urls(prefix=prefix))

    if MetricsPublicAPIInterface.is_auth_enabled():
        urls.append(
            path(
                "robots.txt",
                TemplateView.as_view(
                    template_name="robots.txt", content_type="text/plain"
                ),
            )
        )

    return urls


def _construct_version_one_urls(
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
        path(prefix, PublicAPIRootView.as_view(), name="public-api-root-version-1"),
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


def _construct_version_two_urls(
    *,
    prefix: str,
) -> list[resolvers.URLResolver]:
    """Returns a list of URLResolvers for the public_api version 2

    Args:
        prefix: The prefix to add to the start of the url paths

    Returns:
        List of `URLResolver` objects each representing a
        set of versioned URLS.
    """
    return [
        path(
            f"{prefix}v2/",
            PublicAPIRootViewV2.as_view(),
            name="public-api-v2",
        ),
        path(
            f"{prefix}v2/themes/",
            ThemeListViewV2.as_view(),
            name="theme-list-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>",
            ThemeDetailViewV2.as_view(),
            name="theme-detail-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/",
            SubThemeListViewV2.as_view(),
            name="sub_theme-list-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>",
            SubThemeDetailViewV2.as_view(),
            name="sub_theme-detail-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
            TopicListViewV2.as_view(),
            name="topic-list-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>",
            TopicDetailViewV2.as_view(),
            name="topic-detail-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types",
            GeographyTypeListViewV2.as_view(),
            name="geography_type-list-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>",
            GeographyTypeDetailViewV2.as_view(),
            name="geography_type-detail-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies",
            GeographyListViewV2.as_view(),
            name="geography-list-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>",
            GeographyDetailViewV2.as_view(),
            name="geography-detail-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics",
            MetricListViewV2.as_view(),
            name="metric-list-v2",
        ),
        path(
            f"{prefix}v2/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics/<str:metric>",
            APITimeSeriesViewSetV2.as_view(
                {"get": "list"}, name=APITimeSeriesViewSet.name
            ),
            name="timeseries-list-v2",
        ),
    ]


def _construct_version_three_urls(
    *,
    prefix: str,
) -> list[resolvers.URLResolver]:
    """Returns a list of URLResolvers for the public_api version 3

    Args:
        prefix: The prefix to add to the start of the url paths

    Returns:
        List of `URLResolver` objects each representing a
        set of versioned URLS.
    """

    return [
        path(
            f"{prefix}v3/",
            APITimeSeriesViewSetV3.as_view(
                {"get": "list"}, name=APITimeSeriesViewSetV3.name
            ),
            name="timeseries-list-v3",
        ),
    ]
