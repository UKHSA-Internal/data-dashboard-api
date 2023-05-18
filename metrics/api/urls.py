from django.contrib import admin
from django.urls import include, path, re_path
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
router = routers.DefaultRouter()

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter("wagtailapi")


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (such as pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint("pages", CMSPagesAPIViewSet)


urlpatterns = [
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
    path("health/", HealthView.as_view()),
    path("admin/", admin.site.urls),
    path("api/", api_router.urls),
    path("cms-admin/", include(wagtailadmin_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
