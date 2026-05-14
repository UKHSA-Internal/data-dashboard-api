from datetime import timedelta
from typing import Literal
from urllib.parse import urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.signing import dumps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from wagtail.admin.views.chooser import BrowseView
from wagtail.models import Page

import config
from common.virtual_clock import parse_embargo_time_value


class MissingPreviewFrontendHostConfigurationError(ImproperlyConfigured):
    """Required frontend preview host settings are not configured."""

    def __init__(self) -> None:
        super().__init__("FRONTEND_URL must define an absolute http(s) URL")


class InvalidPreviewFrontendUrlError(ImproperlyConfigured):
    """Preview frontend URL must be an absolute HTTP(S) URL."""

    def __init__(self) -> None:
        super().__init__("Preview redirects must use an absolute http(s) frontend URL")


class PreviewFrontendHostNotAllowedError(ImproperlyConfigured):
    """Preview frontend redirect host is outside the trusted allow-list."""

    def __init__(self) -> None:
        super().__init__(
            "Preview redirect host is not included in the configured allow-list"
        )


class FrontendRedirectView(View):
    """Generate a signed preview token and redirect to the frontend.

    This view is intentionally simple: it performs a permission check on the
    requested page, builds a small payload, signs it using Django's signing
    utilities and then redirects the browser to the frontend with the token as
    a query parameter. The frontend is responsible for validating the token
    and fetching any draft content.

        Preview settings are read at request time from Django settings.

        Security note:
                This endpoint redirects, so it is a security-sensitive sink.
                The implementation is designed to prevent HTTP-forging/open-redirect
                style abuse where an attacker controls the redirect destination.
                In particular:
                - `pk` is constrained by route regex (`[0-9]+`) and must resolve to
                    an existing page.
                - `embargo_time` is untrusted user input but only accepted as `now`
                    or Unix epoch seconds; invalid values are dropped.
                - `slug` and `page_id` are derived server-side from the resolved page,
                    not accepted from query parameters.
                - Final redirect host is validated against a static allow-list from
                    trusted settings before `redirect(...)` is called.
    """

    @staticmethod
    def _get_allowed_frontend_hosts() -> set[str]:
        """Return statically configured hosts allowed for preview redirects.

        Security rationale:
            Preview redirects eventually call Django's redirect helper. If the
            destination host can be influenced by request data or misconfigured
            template values, an attacker can trigger an open redirect and move
            users to a malicious domain that impersonates trusted properties.
            To reduce this risk, we only allow hosts defined in deployment
            configuration and reject everything else.

        Returns:
            set[str]: Allowed host:port values derived from trusted settings.

        Raises:
            ImproperlyConfigured: If no absolute http(s) frontend host can be
                derived from trusted settings.
        """
        configured_urls = {config.FRONTEND_URL}
        allowed_hosts = {
            parts.netloc
            for configured_url in configured_urls
            if configured_url
            and (parts := urlsplit(configured_url)).scheme in {"http", "https"}
            and parts.netloc
        }

        if not allowed_hosts:
            raise MissingPreviewFrontendHostConfigurationError

        return allowed_hosts

    @classmethod
    def validate_frontend_redirect_url(cls, *, frontend_url: str) -> str:
        """Validate the final preview redirect against a trusted host allow-list.

        Security rationale:
            This method prevents open redirect vulnerabilities in the preview
            flow. Even though the URL is built server-side, its shape can still
            be affected by deploy-time configuration. Enforcing an explicit host
            allow-list ensures redirects stay on known frontend domains and do
            not send editors to attacker-controlled sites.

        Args:
            frontend_url: Fully built URL that will be used for redirect.

        Returns:
            str: The same URL when it passes validation.

        Raises:
            ImproperlyConfigured: If the URL is not absolute http(s) or the
                host is not in the configured allow-list.
        """
        parts = urlsplit(frontend_url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise InvalidPreviewFrontendUrlError

        allowed_hosts = cls._get_allowed_frontend_hosts()
        if parts.netloc not in allowed_hosts:
            raise PreviewFrontendHostNotAllowedError

        return frontend_url

    @staticmethod
    def build_redirect_url(
        *,
        raw_url: str,
        slug: str,
        token: str,
        page_id: int,
        embargo_time_value: str | None = None,
    ) -> str:
        """Return preview URL with query params.

        When `embargo_time_value` is supplied it is appended as the `et` query parameter.
        This value is expected to be either a Unix epoch-integer string or the string `now`.
        """
        parts = urlsplit(raw_url)
        params = {"t": token, "page_id": page_id}
        if embargo_time_value is not None:
            params["et"] = embargo_time_value
        query = urlencode(params)
        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                f"{parts.path.rstrip('/')}/{slug}",
                query,
                parts.fragment,
            )
        )

    @staticmethod
    def build_route_slug(*, page: Page) -> str:
        """
        Return the full route path of the page if available,
        otherwise the page slug.
        """
        try:
            _, _, page_path = page.get_url_parts(request=None)
            return (page_path or "").strip("/") or str(page.slug)
        except (AttributeError, TypeError, ValueError):
            return str(page.slug)

    @classmethod
    def build_frontend_route_url(cls, *, base_url: str, route_slug: str) -> str:
        """Build and validate a public frontend route URL for a page.

        This helper is shared between the CMS view and Wagtail hooks to avoid
        drift in URL-shaping behavior.

        Args:
            base_url: Frontend base URL from settings.
            route_slug: Page route slug/path relative to base URL.

        Returns:
            str: Absolute frontend URL ending with a trailing slash.

        Raises:
            ImproperlyConfigured: If the resulting URL is not on the trusted
                frontend host allow-list.
        """
        route_path = route_slug.strip("/")
        frontend_url = (
            f"{base_url.rstrip('/')}/nocache/{route_path}"
            if route_path
            else f"{base_url.rstrip('/')}/nocache"
        )

        # Build it with nocache path - we always view uncached from the CMS
        frontend_url = f"{frontend_url.rstrip('/')}"

        return cls.validate_frontend_redirect_url(frontend_url=frontend_url)

    @classmethod
    def build_frontend_base_url(
        cls, *, base_url: str, route: Literal["preview", "nocache"]
    ) -> str:
        """Build and validate the frontend preview or
            view live (nocache) endpoint URL.

        Args:
            base_url: Frontend base URL from settings.

        Returns:
            str: Absolute frontend `/preview` or `/nocache` endpoint URL.

        Raises:
            ImproperlyConfigured: If the resulting URL is not on the trusted
                frontend host allow-list.
        """

        if route not in {"preview", "nocache"}:
            error_message = "route must be 'preview' or 'nocache'"
            raise ValueError(error_message)

        frontend_url = f"{base_url.rstrip('/')}/{route}"
        return cls.validate_frontend_redirect_url(frontend_url=frontend_url)

    def get(self, request, pk):
        """Generate a short-lived preview token and redirect to the frontend.

        Security rationale:
            The redirect target is always validated before returning the
            response. This blocks open-redirect scenarios where a hostile
            or incorrect URL could send CMS users to an untrusted domain.

                        Input handling summary:
                        - `route` can be only 'preview' or 'nocache' and defaults to 'nocache'
                        - `pk` arrives via a digits-only route and is resolved via
                            `get_object_or_404`, so invalid IDs do not proceed.
                        - `embargo_time` is treated as untrusted and parsed as either
                            `now` or Unix epoch seconds; invalid values are discarded.
                        - `slug` and `page_id` used in the redirect URL are derived from
                            the resolved page object, not direct request parameters.
                        - Redirect destination is accepted only when host/scheme validation
                            succeeds via `validate_frontend_redirect_url`.

        Args:
            request: The HTTP request object
            pk: Primary key of the Page to preview

        Returns:
            HttpResponseRedirect: Redirect to frontend preview URL with signed token

        Raises:
            Http404: If page with given pk does not exist
            PermissionDenied: If user lacks edit permission for the page
        """
        page = get_object_or_404(Page, pk=pk).specific

        perms = page.permissions_for_user(request.user)
        if not perms.can_edit():
            raise PermissionDenied

        embargo_time_value = request.GET.get("embargo_time")
        route = request.GET.get("route", "nocache")

        if route not in {"preview", "nocache"}:
            error_message = (
                "route querystring parameter must be either 'preview' or 'nocache'"
            )
            raise ValueError(error_message)

        parsed_embargo_time = None
        if embargo_time_value is not None:
            embargo_time_value = embargo_time_value.strip()
            if not embargo_time_value:
                embargo_time_value = None
            else:
                parsed_embargo_time = parse_embargo_time_value(embargo_time_value)
                if parsed_embargo_time is None:
                    embargo_time_value = None
                elif embargo_time_value.lower() != "now":
                    embargo_time_value = str(int(embargo_time_value))

        payload = {
            "page_id": page.pk,
            "iat": int(timezone.now().timestamp()),
            "exp": int(
                (
                    timezone.now()
                    + timedelta(seconds=int(settings.PAGE_PREVIEWS_TOKEN_TTL_SECONDS))
                ).timestamp()
            ),
        }

        if parsed_embargo_time is not None:
            payload["embargo_time"] = int(parsed_embargo_time.timestamp())

        token = dumps(payload, salt=settings.PAGE_PREVIEWS_TOKEN_SALT)

        route_slug = self.build_route_slug(page=page)

        frontend_url = self.build_frontend_base_url(
            base_url=config.FRONTEND_URL, route=route
        )

        frontend_url = self.build_redirect_url(
            raw_url=frontend_url,
            slug=route_slug,
            token=token,
            page_id=page.pk,
            embargo_time_value=embargo_time_value,
        )

        return redirect(frontend_url)


class LinkBrowseView(BrowseView):
    def get(
        self, request: WSGIRequest, parent_page_id: int | None = None
    ) -> JsonResponse:
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
