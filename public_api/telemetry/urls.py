from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),
    path("metrics/", views.metrics),
    path("events/", views.events),
]