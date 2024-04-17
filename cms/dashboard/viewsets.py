from django.urls import path
from django.urls.resolvers import RoutePattern
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet

from caching.private_api.decorators import cache_response
from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer


@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = []
    base_serializer_class = ListablePageSerializer
    listing_default_fields = PagesAPIViewSet.listing_default_fields + ["show_in_menus"]

    @cache_response()
    def listing_view(self, request: Request) -> Response:
        """This endpoint returns a list of published pages from the CMS (Wagtail).
        The payload includes page `title`, `id` and `meta` data about each page.
        """
        return super().listing_view(request=request)

    @cache_response()
    def detail_view(self, request: Request, pk: int) -> Response:
        """This end point returns a page from the CMS based on a Page `ID`."""
        return super().detail_view(request=request, pk=pk)


@extend_schema(tags=["cms"])
class CMSDraftPagesViewSet(PagesAPIViewSet):
    base_serializer_class = CMSDraftPagesSerializer
    permission_classes = []

    def detail_view(self, request: Request, pk: int) -> Response:
        """This endpoint returns a page including any unpublished changes in its payload.

        **Note:** this only returns `published` pages with `unpublished` changes.
        """
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


class LinkBrowseView(BrowseView):
    def get(self, request: WSGIRequest, parent_page_id: int | None = None) -> JsonResponse:
        request: WSGIRequest = self._intercept_request_and_switch_off_extra_links(
            request=request
        )
        return super().get(request=request, parent_page_id=parent_page_id)

    @classmethod
    def _intercept_request_and_switch_off_extra_links(
        cls, request: WSGIRequest
    ) -> WSGIRequest:
        intercepted_query_params = request.GET.copy()
        intercepted_query_params["allow_email_link"] = False
        intercepted_query_params["allow_phone_link"] = False
        request.GET = intercepted_query_params
        return request
