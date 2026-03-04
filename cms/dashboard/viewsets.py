from typing import override

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

    @override
    def get_queryset(self):
        """Returns the queryset as per the individual models

        Notes:
            The base class `UKHSAPage` sits between
            Wagtail's `Page` and our page models.
            This includes custom logic for building URLs.
            To give the list endpoint the know-how to build URLs,
            the queryset should be returned as per the individual models.
            Since the models reimplement `get_url_parts()` by virtue
            of the base abstract class `UKHSAPage`

            The use of `specific()` here is horribly inefficient.
            But we already cache this endpoint in Redis,
            so we only pay the penalty once per cache flush.

        Returns:
            Queryset of each page model.
            E.g.
                `<PageQuerySet [<LandingPage: UKHSA data dashboard>, <TopicPage: COVID-19>, ...]>`

        """
        queryset = super().get_queryset()
        return queryset.specific()

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

    @override
    def get_queryset(self):
        """Returns all pages including drafts.

        This endpoint uses Wagtail's `specific()` to return the concrete page
        types so draft revisions can be serialized with their custom fields.

        Returns:
            PageQuerySet: All Page objects, including unpublished drafts, as
                specific model instances.
        """
        return Page.objects.all().specific()

    @staticmethod
    def _normalise_route_slug(*, slug: str) -> str:
        return (slug or "").strip("/")

    def _get_page_for_route_slug(self, *, slug: str) -> Page | None:
        route_slug = self._normalise_route_slug(slug=slug)
        if not route_slug:
            return None

        expected_suffix = f"/{route_slug}/"
        return self.get_queryset().filter(url_path__endswith=expected_suffix).first()

    @classmethod
    def _resolve_page_for_response(
        cls, *, page: Page, show_draft: bool = False
    ) -> Page | None:
        """Resolve a page object for response serialization."""
        if show_draft:
            if page.has_unpublished_changes:
                latest_revision = page.get_latest_revision()
                if latest_revision is not None:
                    return latest_revision.as_object()

            if page.live:
                return page.specific

            return None

        return page.specific

    def get_object(self):
        forced_page = getattr(self, "_forced_detail_page", None)
        if forced_page is not None:
            return forced_page
        return super().get_object()

    def _render_with_existing_detail_pipeline(
        self,
        *,
        request: Request,
        page: Page,
    ) -> Response:
        """Render through the existing PagesAPIViewSet detail pipeline."""
        self._forced_detail_page = page
        try:
            return super().detail_view(request=request, pk=page.pk)
        finally:
            self._forced_detail_page = None

    def detail_view(self, request: Request, slug: str) -> Response:
        """Returns a page including any unpublished changes (draft preview).

        Validates the preview token from the Authorization header before returning
        the latest revision of the requested page. This enables CMS editors to
        preview unpublished changes while restricting access to authorized callers.

        Note:
            This only returns published pages with unpublished changes.

        Args:
            request: The HTTP request with an Authorization header containing a
                Bearer token.
            slug: The page slug to preview.

        Returns:
            Response: JSON payload with the latest revision, or HTTP 401 if
                authorization fails.
        """
        auth = request.headers.get("Authorization", "")
        if not auth or not auth.lower().startswith("bearer "):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = loads(token, salt=PAGE_PREVIEWS_TOKEN_SALT)
        except (BadSignature, SignatureExpired, ValueError, TypeError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        exp = payload.get("exp")
        if exp is None or timezone.now().timestamp() > exp:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        instance = self._get_page_for_route_slug(slug=slug)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        payload_page_id = payload.get("page_id")
        if payload_page_id is None or int(payload_page_id) != int(instance.pk):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        page_for_response = self._resolve_page_for_response(
            page=instance,
            show_draft=True,
        )
        if page_for_response is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return self._render_with_existing_detail_pipeline(
            request=request,
            page=page_for_response,
        )

    @classmethod
    def get_urlpatterns(cls) -> list[RoutePattern]:
        """This returns a list of URL patterns for the viewset.

        Notes:
            Only the detail `/{slug}` path is included.

        """
        return [
            path("<path:slug>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
