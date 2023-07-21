from django.urls import path
from django.urls.resolvers import RoutePattern
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
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

    def detail_view(self, request: Request, pk: int) -> Response:
        instance = self.get_object()
        instance = instance.get_latest_revision_as_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @classmethod
    def get_urlpatterns(cls) -> list[RoutePattern]:
        """This returns a list of URL patterns for the viewset.

        Notes:
            Only the detail `/{id}` path is included.

        """
        return [
            path("<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
