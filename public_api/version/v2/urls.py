from django.urls import path, resolvers
from public_api.version.v2.views import (
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
from public_api.views.timeseries_viewset import APITimeSeriesViewSet
from public_api.version.v2.views.timeseries_viewset import APITimeSeriesViewSetV2


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
