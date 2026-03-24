from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^api/telemetry/events", views.events),
    re_path(r"^api/telemetry/metrics", views.metrics),
    re_path(r"^api/telemetry/health", views.health),
]