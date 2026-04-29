from typing import override

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet

from caching.private_api.decorators import cache_response
from cms.dashboard.serializers import ListablePageSerializer
from validation.shared import (
    get_cms_auth_bearer_token,
    get_cms_auth_payload,
    validate_preview_hmac_token,
)


@extend_schema(tags=["cms"])
class BaseCMSPagesAPIViewSet(PagesAPIViewSet):
    """Shared CMS pages API behavior for published and draft endpoints."""

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
    """Cached API viewset for published CMS pages."""

    @cache_response()
    def listing_view(self, request: Request) -> Response:
        """Return the cached published page listing response."""
        return super().listing_view(request)

    @cache_response()
    def detail_view(self, request: Request, pk: int) -> Response:
        """Return the cached published page detail response."""
        return super().detail_view(request, pk)


@extend_schema(tags=["cms"])
class CMSDraftPagesViewSet(BaseCMSPagesAPIViewSet):
    """API viewset for authenticated draft page preview responses."""

    INVALID_TOKEN_DETAIL = {"detail": "The token was invalid"}

    @staticmethod
    def _with_embargo_time(data: dict, embargo_time: int | None) -> dict:
        """Add embargo_time field to serialized page data.

        Args:
            data: The serialized page response data.
            embargo_time: Unix timestamp or None if no embargo is set.

        Returns:
            A copy of data with the embargo_time field added.
        """
        response_data = dict(data)
        response_data["embargo_time"] = embargo_time
        return response_data

    @override
    def detail_view(self, request: Request, pk: int) -> Response:
        """Retrieve a draft page by ID with HMAC token validation.

        This endpoint serves pre-signed preview tokens from the CMS admin.
        It validates the token, applies any embargo time, and returns either
        the latest draft revision (if available) or the published page.

        Args:
            request: The HTTP request containing the authentication token
                     in the x-cms-auth header.
            pk: The primary key of the page to retrieve.

        Returns:
            Response with:
                - 200: Page detail with embargo_time field set.
                - 401: Invalid or missing token.
                - 403: PAGE_PREVIEWS_ENABLED is False.
                - 404: Page not found.
                - 501: Embargo Date (embargo_time) not supported.
        """
        # Check if previews are enabled
        page_previews_enabled = getattr(settings, "PAGE_PREVIEWS_ENABLED", False)
        if not page_previews_enabled:
            return Response(
                {
                    "detail": "Page previews are disabled.  Contact your site administrator for more information."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Require Bearer token in x-cms-auth header
        token = get_cms_auth_bearer_token(request.headers)
        if token is None:
            return Response(
                self.INVALID_TOKEN_DETAIL, status=status.HTTP_401_UNAUTHORIZED
            )

        # Validate token once and optionally receive decoded payload.
        validation_result = validate_preview_hmac_token(
            token,
            page_id=pk,
            include_payload=True,
        )
        if not validation_result:
            return Response(
                self.INVALID_TOKEN_DETAIL, status=status.HTTP_401_UNAUTHORIZED
            )
        payload = (
            validation_result
            if isinstance(validation_result, dict)
            else (get_cms_auth_payload(token) or {})
        )

        # Middleware already sets request-scoped embargo time when applicable.
        embargo_time = payload.get("embargo_time")

        # Get page instance
        instance = self.get_queryset().filter(pk=pk).first()
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Return latest draft if available, else published
        latest_revision = instance.get_latest_revision()
        if latest_revision:
            instance = latest_revision.as_object()
        serializer = self.get_serializer(instance)
        return Response(self._with_embargo_time(serializer.data, embargo_time))
