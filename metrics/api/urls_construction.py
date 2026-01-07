from django.contrib import admin
from django.urls import include, path, re_path, resolvers
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.api.v2.router import WagtailAPIRouter

from cms.dashboard.views import LinkBrowseView
from cms.dashboard.viewsets import CMSDraftPagesViewSet, CMSPagesAPIViewSet
from cms.snippets.views import GlobalBannerView, MenuView
from feedback.api.urls import construct_urlpatterns_for_feedback
from metrics.api import enums, settings
from metrics.api.views import (
    AuditAPITimeSeriesViewSet,
    AuditCoreHeadlineViewSet,
    AuditCoreTimeseriesViewSet,
    BulkDownloadsView,
    ChartsView,
    ColdAlertViewSet,
    DownloadsView,
    EncodedChartsView,
    HeadlinesView,
    HealthView,
    HeatAlertViewSet,
    SubplotDownloadsView,
    TablesSubplotView,
    TablesView,
    TrendsView,
)
from metrics.api.views.charts import DualCategoryChartsView
from metrics.api.views.charts.subplot_charts import SubplotChartsView
from metrics.api.views.geographies import GeographiesView, GeographiesViewDeprecated
from metrics.api.views.health import InternalHealthView
from metrics.api.views.maps import MapsView
from public_api import construct_url_patterns_for_public_api

router = routers.DefaultRouter()

# Create the router. "wagtailapi" is the URL namespace
cms_api_router = WagtailAPIRouter("wagtailapi")


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (such as pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
cms_api_router.register_endpoint("pages", CMSPagesAPIViewSet)
cms_api_router.register_endpoint("drafts", CMSDraftPagesViewSet)


def construct_cms_admin_urlpatterns(
    *,
    app_mode: str | None,
) -> list[resolvers.URLResolver]:
    """Builds a list of `URLResolver` instances for the cms-admin application module

    Notes:
        If the `app_mode` argument is not equal to `CMS_ADMIN`,
        then this function will return the URL at the designated path
        i.e. "/cms-admin/
        Otherwise, if the `app_mode` argument is equal to `CMS_ADMIN`,
        the returned URL will be at the root i.e. "/"

    Args:
        app_mode: The 'mode' in which the application is currently in.
            This can be provided via the `APP_MODE` environment variable.

    Returns:
        List of `URLResolver` object which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    prefix: str = "" if app_mode == enums.AppMode.CMS_ADMIN.value else "cms-admin/"
    return [
        path(prefix, include(wagtailadmin_urls)),
        path("choose-page/", LinkBrowseView.as_view(), name="wagtailadmin_choose_page"),
    ]


DEFAULT_PUBLIC_API_PREFIX = "api/public/timeseries/"


def construct_public_api_urlpatterns(
    *,
    app_mode: str | None,
) -> list[resolvers.URLResolver]:
    """Builds a list of `URLResolver` instances for the public API application module

    Notes:
        If the `app_mode` argument is not equal to `PUBLIC_API`,
        then this function will return the URL at the designated path
        i.e. "/api/public/timeseries/"
        Otherwise, if the `app_mode` argument is equal to `PUBLIC_API`,
        the returned URL will be at the root i.e. "/"

    Args:
        app_mode: The 'mode' in which the application is currently in.
            This can be provided via the `APP_MODE` environment variable.

    Returns:
        List of `URLResolver` object which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    prefix: str = (
        "" if app_mode == enums.AppMode.PUBLIC_API.value else DEFAULT_PUBLIC_API_PREFIX
    )

    return construct_url_patterns_for_public_api(prefix=prefix)


API_PREFIX = "api/"

heat_alert_list = HeatAlertViewSet.as_view({"get": "list"})
heat_alert_detail = HeatAlertViewSet.as_view({"get": "retrieve"})
cold_alert_list = ColdAlertViewSet.as_view({"get": "list"})
cold_alert_detail = ColdAlertViewSet.as_view({"get": "retrieve"})

private_api_urlpatterns = [
    # Headless CMS API - pages + drafts endpoints
    path(API_PREFIX, cms_api_router.urls),
    path(f"{API_PREFIX}global-banners/v2", GlobalBannerView.as_view()),
    path(f"{API_PREFIX}menus/v1", MenuView.as_view()),
    path(f"{API_PREFIX}alerts/v1/heat", heat_alert_list, name="heat-alerts-list"),
    path(
        f"{API_PREFIX}alerts/v1/heat/<str:geography_code>",
        heat_alert_detail,
        name="heat-alerts-detail",
    ),
    path(f"{API_PREFIX}alerts/v1/cold", cold_alert_list, name="cold-alerts-list"),
    path(
        f"{API_PREFIX}alerts/v1/cold/<str:geography_code>",
        cold_alert_detail,
        name="cold-alerts-detail",
    ),
    # Metrics/private content endpoints
    re_path(f"^{API_PREFIX}charts/v3", EncodedChartsView.as_view()),
    re_path(f"^{API_PREFIX}charts/subplot/v1", SubplotChartsView.as_view()),
    re_path(f"^{API_PREFIX}downloads/v2", DownloadsView.as_view()),
    re_path(f"^{API_PREFIX}bulkdownloads/v1", BulkDownloadsView.as_view()),
    re_path(f"^{API_PREFIX}downloads/subplot/v1", SubplotDownloadsView.as_view()),
    re_path(
        f"^{API_PREFIX}geographies/v2/(?P<topic>[^/]+)",
        GeographiesViewDeprecated.as_view(),
    ),
    re_path(f"^{API_PREFIX}geographies/v3", GeographiesView.as_view()),
    re_path(f"^{API_PREFIX}headlines/v3", HeadlinesView.as_view()),
    re_path(f"^{API_PREFIX}maps/v1", MapsView.as_view()),
    re_path(f"^{API_PREFIX}tables/v4", TablesView.as_view()),
    re_path(f"^{API_PREFIX}tables/subplot/v1", TablesSubplotView.as_view()),
    re_path(f"^{API_PREFIX}trends/v3", TrendsView.as_view()),
]

# Audit API endpoints
audit_api_timeseries_list = AuditAPITimeSeriesViewSet.as_view({"get": "list"})
audit_core_timeseries_list = AuditCoreTimeseriesViewSet.as_view({"get": "list"})
audit_api_core_headline_list = AuditCoreHeadlineViewSet.as_view({"get": "list"})

audit_api_urlpatterns = [
    path(
        f"{API_PREFIX}audit/v1/api-timeseries/<str:metric>/<str:geography_type>/<str:geography>/<str:stratum>/<str:sex>/<str:age>",
        audit_api_timeseries_list,
        name="audit-api-timeseries",
    ),
    path(
        f"{API_PREFIX}audit/v1/core-timeseries/<str:metric>/<str:geography_type>/<str:geography>/<str:stratum>/<str:sex>/<str:age>",
        audit_core_timeseries_list,
        name="audit-core-timeseries",
    ),
    path(
        f"{API_PREFIX}audit/v1/core-headline/<str:metric>/<str:geography_type>/<str:geography>/<str:stratum>/<str:sex>/<str:age>",
        audit_api_core_headline_list,
        name="audit-core-headline",
    ),
    re_path(f"^{API_PREFIX}charts/v2", ChartsView.as_view()),
    re_path(f"^{API_PREFIX}charts/v3", EncodedChartsView.as_view()),
    re_path(f"^{API_PREFIX}charts/dual-category/v1", DualCategoryChartsView.as_view()),
]

feedback_urlpatterns = construct_urlpatterns_for_feedback(prefix=API_PREFIX)

docs_urlspatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # JSON schema view
    path("api/schema", SpectacularJSONAPIView.as_view(), name="schema"),
    # Swagger docs UI schema view:
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc schema view
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

static_urlpatterns = [
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]

common_urlpatterns = [
    # Health probe
    path("health/", HealthView.as_view()),
    # Internal health probe
    path(".well-known/health-check/", InternalHealthView.as_view()),
    # Static files
    path("", include(static_urlpatterns)),
]

django_admin_urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
]


def construct_urlpatterns(
    *,
    app_mode: str | None,
) -> list[resolvers.URLResolver, resolvers.URLPattern]:
    """Builds a list of `URLResolver` and `URLPattern` instances for the django app to consume.

    Notes:
        If the `app_mode` argument is not one of the following:
            - `CMS_ADMIN`
            - `PRIVATE_API`
            - `PUBLIC_API`
            - `FEEDBACK_API`
            - `INGESTION`
        Then this function will return the complete set of URLs.

    Args:
        app_mode: The 'mode' in which the application is currently in.
            This can be provided via the `APP_MODE` environment variable.

    Returns:
        List of `URLResolver` and `URLPattern` objects which
        can then be consumed by the django application
        via `urlpatterns` in `urls.py`

    """
    # Base urls required for each workload type
    constructed_url_patterns = (
        docs_urlspatterns + static_urlpatterns + common_urlpatterns
    )

    match app_mode:
        case enums.AppMode.CMS_ADMIN.value:
            constructed_url_patterns += django_admin_urlpatterns
            constructed_url_patterns += construct_cms_admin_urlpatterns(
                app_mode=app_mode
            )
            constructed_url_patterns += audit_api_urlpatterns
        case enums.AppMode.PUBLIC_API.value:
            constructed_url_patterns += construct_public_api_urlpatterns(
                app_mode=app_mode
            )
        case enums.AppMode.PRIVATE_API.value:
            constructed_url_patterns += private_api_urlpatterns
        case enums.AppMode.FEEDBACK_API.value:
            constructed_url_patterns += feedback_urlpatterns
        case enums.AppMode.INGESTION.value:
            # Ingestion mode does not expose any endpoints
            return constructed_url_patterns
        case _:
            constructed_url_patterns += construct_cms_admin_urlpatterns(
                app_mode=app_mode
            )
            constructed_url_patterns += construct_public_api_urlpatterns(
                app_mode=app_mode
            )
            constructed_url_patterns += django_admin_urlpatterns
            constructed_url_patterns += private_api_urlpatterns
            constructed_url_patterns += feedback_urlpatterns
            constructed_url_patterns += audit_api_urlpatterns

    return constructed_url_patterns
