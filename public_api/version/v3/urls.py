from django.db import models
from django.urls import path, resolvers

from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.views.timeseries_viewset import APITimeSeriesViewSet
from public_api.version.v3.views.timeseries_viewset import APITimeSeriesViewSetV3
from public_api.version.v3.views import (
    GeographyDetailViewV3,
    GeographyListViewV3,
    GeographyTypeDetailViewV3,
    GeographyTypeListViewV3,
    MetricListViewV3,
    PublicAPIRootViewV3,
    SubThemeDetailViewV3,
    SubThemeListViewV3,
    ThemeDetailViewV3,
    ThemeListViewV3,
    TopicDetailViewV3,
    TopicListViewV3,
)


def _construct_urls(
    *, prefix: str, queryset: models.Queryset
) -> list[resolvers.URLResolver]:
    return [
        path(
            f"{prefix}/",
            PublicAPIRootViewV3.as_view(),
            name=f"public-api-v3",
        ),
        path(
            f"{prefix}/themes/",
            ThemeListViewV3.as_view(queryset=queryset),
            name=f"theme-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>",
            ThemeDetailViewV3.as_view(queryset=queryset),
            name=f"theme-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/",
            SubThemeListViewV3.as_view(queryset=queryset),
            name=f"sub_theme-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>",
            SubThemeDetailViewV3.as_view(queryset=queryset),
            name=f"sub_theme-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
            TopicListViewV3.as_view(queryset=queryset),
            name=f"topic-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>",
            TopicDetailViewV3.as_view(queryset=queryset),
            name=f"topic-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types",
            GeographyTypeListViewV3.as_view(queryset=queryset),
            name=f"geography_type-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>",
            GeographyTypeDetailViewV3.as_view(queryset=queryset),
            name=f"geography_type-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies",
            GeographyListViewV3.as_view(queryset=queryset),
            name=f"geography-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>",
            GeographyDetailViewV3.as_view(queryset=queryset),
            name=f"geography-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics",
            MetricListViewV3.as_view(queryset=queryset),
            name=f"metric-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics/<str:metric>",
            APITimeSeriesViewSetV3.as_view(
                {"get": "list"}, name=APITimeSeriesViewSet.name
            ),
            name=f"timeseries-list-v3",
        ),
    ]


def construct_version_three_urls(
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

    return (
        [
            path(
                f"{prefix}/",
                PublicAPIRootViewV3.as_view(),
                name=f"public-api-v3",
            ),
        ]
        + _construct_urls(
            prefix=f"{prefix}/timeseries",
            queryset=MetricsPublicAPIInterface.get_api_timeseries_model().objects.all(),
        )
        + _construct_urls(
            prefix=f"{prefix}/headline",
            queryset=MetricsPublicAPIInterface.get_api_headline_model().objects.all(),
        )
    )
