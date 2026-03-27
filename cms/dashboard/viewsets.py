import datetime
from django.utils import timezone
from typing import override

from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, loads
from validation.shared import validate_preview_hmac_token
from cms.dashboard.virtual_clock import set_embargo_time, clear_embargo_time
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet

from caching.private_api.decorators import cache_response
from cms.dashboard.serializers import ListablePageSerializer

PAGE_PREVIEWS_TOKEN_SALT = getattr(
    settings, "PAGE_PREVIEWS_TOKEN_SALT", "preview-token"
)


@extend_schema(tags=["cms"])
class BaseCMSPagesAPIViewSet(PagesAPIViewSet):
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

    def listing_view(self, request: Request) -> Response:
        """This endpoint returns a list of published pages from the CMS (Wagtail).
        The payload includes page `title`, `id` and `meta` data about each page.
        """
        return super().listing_view(request=request)

    def detail_view(self, request: Request, pk: int) -> Response:
        """This end point returns a page from the CMS based on a Page `ID`."""
        return super().detail_view(request=request, pk=pk)


@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(BaseCMSPagesAPIViewSet):
    @cache_response()
    def listing_view(self, request: Request) -> Response:
        return super().listing_view(request)

    @cache_response()
    def detail_view(self, request: Request, pk: int) -> Response:
        return super().detail_view(request, pk)


@extend_schema(tags=["cms"])
class CMSDraftPagesViewSet(BaseCMSPagesAPIViewSet):
    @override
    def detail_view(self, request: Request, pk: int) -> Response:
        # Check if previews are enabled
        page_previews_enabled = getattr(settings, "PAGE_PREVIEWS_ENABLED", False)
        if not page_previews_enabled:
            return Response(
                {
                    "detail": "Page previews are disabled.  Contact your site administrator for more information."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Require Bearer token in x-draft-auth header
        auth = request.headers.get("x-draft-auth", "")
        if not auth or not auth.lower().startswith("bearer "):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # Validate and decode token using shared logic
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = validate_preview_hmac_token(token, page_id=pk)
        except ValueError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # If present, set embargo_time in virtual_clock 
        embargo_time = payload.get("embargo_time")
        if embargo_time is not None:
            dt_utc = datetime.datetime.fromtimestamp(embargo_time, tz=datetime.timezone.utc)
            set_embargo_time(dt_utc)
        else:
            # Defensive: contextvars are per-request, 
            # but we clear embargo_time to be absolutely certain
            clear_embargo_time()

        # Get page instance
        instance = self.get_queryset().filter(pk=pk).first()
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Return latest draft if available, else published
        latest_revision = instance.get_latest_revision()
        if latest_revision:
            draft_page = latest_revision.as_object()
            serializer = self.get_serializer(draft_page)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
