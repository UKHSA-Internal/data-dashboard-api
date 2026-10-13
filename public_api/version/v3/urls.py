from django.urls import path, resolvers
from rest_framework import serializers

from public_api.version.v3.serializers.serializers import (
    APIHeadlineListSerializerv3,
    APITimeSeriesListSerializerv3,
)
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
from public_api.version.v3.views.viewset import APIViewSetV3


def _construct_urls(
    *, prefix: str, url_prefix: str, serializer_class: serializers.ModelSerializer
) -> list[resolvers.URLPattern]:
    return [
        path(
            f"{prefix}/themes/",
            ThemeListViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-theme-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>",
            ThemeDetailViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-theme-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/",
            SubThemeListViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-sub_theme-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>",
            SubThemeDetailViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-sub_theme-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
            TopicListViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-topic-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>",
            TopicDetailViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-topic-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types",
            GeographyTypeListViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-geography_type-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>",
            GeographyTypeDetailViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-geography_type-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies",
            GeographyListViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-geography-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>",
            GeographyDetailViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-geography-detail-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics",
            MetricListViewV3.as_view(
                api_model=serializer_class.Meta.model, url_prefix=url_prefix
            ),
            name=f"{url_prefix}-metric-list-v3",
        ),
        path(
            f"{prefix}/themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>/geography_types/<str:geography_type>/geographies/<str:geography>/metrics/<str:metric>",
            APIViewSetV3.as_view(
                {"get": "list"},
                name=APIViewSetV3.name,
                serializer_class=serializer_class,
            ),
            name=f"{url_prefix}-metric-detail-v3",
        ),
    ]


def construct_version_three_urls(
    *,
    prefix: str,
) -> list[resolvers.URLPattern]:
    """Returns a list of URLResolvers for the public_api version 2

    Notes:
        `DEFAULT_PUBLIC_API_PREFIX` is swapped out for an empty string on
        deployed instances of the public_api. This Constant is only used for
        local development.

        Due to the removal of `timeseries/` as a default part of the prefix
        in V3 now that `headline` has been integrated.
        There is an override included below to leave V1 and V2 as they
        are for now. This override will be removed when V2 is deprecated.
        see: `metrics/api/urls_contruction` LN 105 for reference.

    Args:
        prefix: The prefix to add to the start of the url paths

    Returns:
        List of `URLResolver` objects each representing a
        set of versioned URLS.
    """

    # Temporary fix for the public_url prefix until v2 is deprecated - see Notes: in docstring
    prefix = "api/public/" if prefix == "api/public/timeseries/" else prefix

    return (
        [
            path(
                f"{prefix}v3/",
                PublicAPIRootViewV3.as_view(),
                name="public-api-v3",
            ),
        ]
        + _construct_urls(
            prefix=f"{prefix}v3/timeseries",
            url_prefix="timeseries",
            serializer_class=APITimeSeriesListSerializerv3,
        )
        + _construct_urls(
            prefix=f"{prefix}v3/headline",
            url_prefix="headline",
            serializer_class=APIHeadlineListSerializerv3,
        )
    )
