from django.urls import path

from metrics.public_api.views import (
    PublicAPIRootView,
    SubThemeDetailView,
    SubThemeListView,
    ThemeDetailView,
    ThemeListView,
    TopicDetailView,
    TopicListView,
)

PUBLIC_API_PREFIX = "api/public/timeseries/"


urlpatterns = [
    path(PUBLIC_API_PREFIX, PublicAPIRootView.as_view(), name="public-api-root"),
    path(f"{PUBLIC_API_PREFIX}themes/", ThemeListView.as_view(), name="theme-list"),
    path(
        f"{PUBLIC_API_PREFIX}themes/<str:theme>",
        ThemeDetailView.as_view(),
        name="theme-detail",
    ),
    path(
        f"{PUBLIC_API_PREFIX}themes/<str:theme>/sub_themes/",
        SubThemeListView.as_view(),
        name="sub_theme-list",
    ),
    path(
        f"{PUBLIC_API_PREFIX}themes/<str:theme>/sub_themes/<str:sub_theme>",
        SubThemeDetailView.as_view(),
        name="sub_theme-detail",
    ),
    path(
        f"{PUBLIC_API_PREFIX}themes/<str:theme>/sub_themes/<str:sub_theme>/topics",
        TopicListView.as_view(),
        name="topic-list",
    ),
    path(
        f"{PUBLIC_API_PREFIX}themes/<str:theme>/sub_themes/<str:sub_theme>/topics/<str:topic>",
        TopicDetailView.as_view(),
        name="topic-detail",
    ),
]
