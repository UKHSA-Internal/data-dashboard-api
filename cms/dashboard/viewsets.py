from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from wagtail.api.v2.views import PagesAPIViewSet

from cms.dashboard.serializers import CMSDraftPagesSerializer


@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = [HasAPIKey]


@extend_schema(tags=["cms"])
class CMSDraftPagesViewSet(PagesAPIViewSet):
    base_serializer_class = CMSDraftPagesSerializer
    permission_classes = [HasAPIKey]

    def detail_view(self, request, pk):
        instance = self.get_object()
        instance = instance.get_latest_revision_as_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path("<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
