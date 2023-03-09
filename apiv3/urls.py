from django.urls import path, include, re_path
from django.contrib import admin
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apiv3.viewsets import WeeklyTimeSeriesViewSet
from apiv3.views import FileUploadView, GraphView, ItemView, ChartView

router = routers.DefaultRouter()
router.register(r'weeklytimeseries', WeeklyTimeSeriesViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(router.urls)),
    path('items/', ItemView.as_view()),
    path('graph/', GraphView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view()),
    re_path(r'^chart/(?P<topic>[^/]+)$', ChartView.as_view()),
    path('admin/', admin.site.urls),
]