from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, loads
from django.urls import path
from django.urls.resolvers import RoutePattern
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Page

from caching.private_api.decorators import cache_response
from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer

PAGE_PREVIEWS_TOKEN_SALT = getattr(
    settings, "PAGE_PREVIEWS_TOKEN_SALT", "preview-token"
)


@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = []
    base_serializer_class = ListablePageSerializer
    listing_default_fields = PagesAPIViewSet.listing_default_fields + ["show_in_menus"]
    detail_only_fields = []

    def get_queryset(self):
        """Returns the queryset as per the individual models.

        The base class `UKHSAPage` sits between Wagtail's `Page` and our page models,
        implementing custom logic for building URLs. The queryset must return specific
        model instances (e.g., LandingPage, TopicPage) rather than generic Page objects
        so the API can access the custom `get_url_parts()` method defined in UKHSAPage.

        The use of `specific()` here is horribly inefficient, causing N+1 queries or
        expensive JOINs. However, this endpoint is cached in Redis with @cache_response(),
        so we only pay the penalty once per cache flush.

        Returns:
            PageQuerySet: A queryset of specific page model instances.
                Example: <PageQuerySet [<LandingPage: UKHSA data dashboard>, <TopicPage: COVID-19>, ...]>
        """
        queryset = super().get_queryset()
        return queryset.specific()

    @cache_response()
    def listing_view(self, request: Request) -> Response:
        """Returns a list of published pages from the CMS.

        Args:
            request: The HTTP request object

        Returns:
            Response: JSON payload with page title, id, and metadata for each page
        """
        return super().listing_view(request=request)

    @cache_response()
    def detail_view(self, request: Request, pk: int) -> Response:
        """Returns a single page from the CMS by ID.

        Args:
            request: The HTTP request object
            pk: The page ID to retrieve

        Returns:
            Response: JSON payload with page details
        """
        return super().detail_view(request=request, pk=pk)


@extend_schema(tags=["cms"])
class CMSDraftPagesViewSet(PagesAPIViewSet):
    base_serializer_class = CMSDraftPagesSerializer
    permission_classes = []

    def get_queryset(self):
        """Returns all pages including drafts.

        Returns:
            PageQuerySet: All Page objects including unpublished drafts as specific model instances
        """
        return Page.objects.all().specific()

    def detail_view(self, request: Request, pk: int) -> Response:
        """Returns a page including any unpublished changes (draft preview).

        Validates the preview token from the Authorization header before returning
        the latest revision of the requested page. This enables CMS editors to preview
        their unpublished changes.

        Note:
            This only returns published pages with unpublished changes.

        Args:
            request: The HTTP request with Authorization header containing Bearer token
            pk: The page ID to preview

        Returns:
            Response: JSON payload with draft page content, or HTTP 401 if unauthorized
        """
        auth = request.headers.get("Authorization", "")
        if not auth or not auth.lower().startswith("bearer "):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = loads(token, salt=PAGE_PREVIEWS_TOKEN_SALT)
        except (BadSignature, SignatureExpired, ValueError, TypeError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        payload_page_id = payload.get("page_id")
        if payload_page_id is None or int(payload_page_id) != int(pk):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        exp = payload.get("exp")
        if exp is None or timezone.now().timestamp() > exp:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        instance = instance.get_latest_revision_as_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @classmethod
    def get_urlpatterns(cls) -> list[RoutePattern]:
        """Returns URL patterns for the draft pages viewset.

        Only the detail endpoint is exposed (no list view for drafts).

        Returns:
            list[RoutePattern]: URL pattern for the detail view at /<int:pk>/
        """
        return [
            path("<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
