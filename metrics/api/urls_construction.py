from typing import List, Optional, Union

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

from cms.dashboard.viewsets import CMSPagesAPIViewSet
from metrics.api import settings
from metrics.api.views import (
    ChartsView,
    DownloadsView,
    FileUploadView,
    HeadlinesView,
    HealthView,
    OldTabularView,
    TablesView,
    TrendsView,
)
from metrics.public_api.urls import urlpatterns as public_api_urlpatterns

router = routers.DefaultRouter()

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter("wagtailapi")


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (such as pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint("pages", CMSPagesAPIViewSet)

cms_api_urlpatterns = [
    # CMS pages endpoints
    path("api/", api_router.urls),
    # Serves the CMS admin view
    path("cms-admin/", include(wagtailadmin_urls)),
]

API_PREFIX = "api/"

private_api_urlpatterns = [
    re_path(f"^{API_PREFIX}upload/", FileUploadView.as_view()),
    re_path(f"^{API_PREFIX}charts/v2", ChartsView.as_view()),
    re_path(f"^{API_PREFIX}downloads/v2", DownloadsView.as_view()),
    re_path(f"^{API_PREFIX}headlines/v2", HeadlinesView.as_view()),
    re_path(
        f"^{API_PREFIX}tabular/(?P<topic>[^/]+)/(?P<metric>[^/]+)$",
        OldTabularView.as_view(),
    ),
    re_path(f"^{API_PREFIX}tables/v2", TablesView.as_view()),
    re_path(f"^{API_PREFIX}trends/v2", TrendsView.as_view()),
    # Endpoints to be migrated away from
    re_path(r"^upload/$", FileUploadView.as_view()),
    re_path(r"^charts/v2", ChartsView.as_view()),
    re_path(r"^downloads/v2", DownloadsView.as_view()),
    re_path(r"^headlines/v2", HeadlinesView.as_view()),
    re_path(
        r"^tabular/(?P<topic>[^/]+)/(?P<metric>[^/]+)$",
        OldTabularView.as_view(),
    ),
    re_path(r"^tables/v2", TablesView.as_view()),
    re_path(r"^trends/v2", TrendsView.as_view()),
]

docs_urlspatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # JSON schema view
    path("api/schema/", SpectacularJSONAPIView.as_view(), name="schema"),
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
    # Static files
    path("", include(static_urlpatterns)),
]

django_admin_urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
]


def construct_urlpatterns(
    app_mode: Optional[str],
) -> List[Union[resolvers.URLResolver, resolvers.URLPattern]]:
    """Builds a list of `URLResolver` and `URLPattern` instances for the django app to consume.

    Notes:
        If the `app_mode` argument is not one of the following:
            - `CMS`
            - `PRIVATE_API`
            - `PUBLIC_API`
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

    if app_mode == "CMS":
        constructed_url_patterns += cms_api_urlpatterns
        constructed_url_patterns += django_admin_urlpatterns
    elif app_mode == "PUBLIC_API":
        constructed_url_patterns += public_api_urlpatterns
    elif app_mode == "PRIVATE_API":
        constructed_url_patterns += private_api_urlpatterns
    else:
        constructed_url_patterns += cms_api_urlpatterns
        constructed_url_patterns += django_admin_urlpatterns
        constructed_url_patterns += public_api_urlpatterns
        constructed_url_patterns += private_api_urlpatterns

    return constructed_url_patterns
