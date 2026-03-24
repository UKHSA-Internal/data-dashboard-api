from django.urls import path
from . import views

urlpatterns = [
    path("api/telemetry/events", views.events),
    path("api/telemetry/metrics", views.metrics),
    path("api/telemetry/health", views.health),
]