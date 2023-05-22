from django.urls import path

from metrics.public_api.views import ThemeDetailView, ThemeListView, public_api_root

PUBLIC_API_PREFIX = "api/public/timeseries/"


urlpatterns = [
    path(PUBLIC_API_PREFIX, public_api_root, name="public-api-root"),
    path(f"{PUBLIC_API_PREFIX}themes/", ThemeListView.as_view(), name="theme-list"),
    path(
        f"{PUBLIC_API_PREFIX}themes/<str:theme>",
        ThemeDetailView.as_view(),
        name="theme-detail",
    ),
]
