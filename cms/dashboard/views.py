from datetime import timedelta
from urllib.parse import urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.signing import dumps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from wagtail.admin.views.chooser import BrowseView
from wagtail.models import Page

# Token salt for preview tokens; configurable via Django settings to avoid
# hard-coded strings in code.
PAGE_PREVIEWS_TOKEN_SALT = getattr(
    settings, "PAGE_PREVIEWS_TOKEN_SALT", "preview-token"
)


class PreviewToFrontendRedirectView(View):
    """Generate a signed preview token and redirect to the frontend.

    This view is intentionally simple: it performs a permission check on the
    requested page, builds a small payload, signs it using Django's signing
    utilities and then redirects the browser to the frontend with the token as
    a query parameter. The frontend is responsible for validating the token
    and fetching any draft content.

    Attributes:
        PREVIEW_TOKEN_TTL_SECONDS: Token lifetime in seconds (configurable via
            PAGE_PREVIEWS_TOKEN_TTL_SECONDS setting, defaults to 120)
    """

    # token lifetime in seconds (configurable via settings)
    PREVIEW_TOKEN_TTL_SECONDS = getattr(
        settings,
        "PAGE_PREVIEWS_TOKEN_TTL_SECONDS",
        120,
    )

    @staticmethod
    def _canonicalise_preview_url(*, raw_url: str, slug: str, token: str, page_id: int) -> str:
        """Return preview URL with canonical query params.

        The query string is always normalised to `slug`, `t`, and `page_id` so stale or
        legacy template parameters (e.g. `draft=true`, `slug_name`) are not propagated to the frontend.
        """
        parts = urlsplit(raw_url)
        query = urlencode({"slug": slug, "t": token, "page_id": page_id})
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, query, parts.fragment)
        )

    @staticmethod
    def build_route_slug(*, page: Page) -> str:
        """Return route-style slug path matching frontend route shape.

        For nested pages this returns paths like `parent/child` (matching
        `html_url` path semantics) rather than a leaf-only slug.
        """
        route_path = ""
        try:
            _, _, page_path = page.get_url_parts(request=None)
            route_path = (page_path or "").strip("/")
        except (AttributeError, TypeError, ValueError):
            route_path = ""

        return route_path or str(page.slug)

    def get(self, request, pk):
        """Handle GET request to generate preview token and redirect to frontend.

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

        now = timezone.now()
        payload = {
            "page_id": page.pk,
            "editor_id": request.user.pk if request.user.is_authenticated else None,
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(seconds=self.PREVIEW_TOKEN_TTL_SECONDS)).timestamp()
            ),
        }

        token = dumps(payload, salt=PAGE_PREVIEWS_TOKEN_SALT)

        # Build the frontend URL using a configurable template. The template
        # should include placeholders for `{slug}` and `{token}`.
        # A default
        # value is provided to preserve previous behaviour.
        # See docs/environment_variables.md for PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE format.
        template = getattr(
            settings,
            "PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE",
            "http://localhost:3000/preview?slug={slug}&t={token}",
        )

        route_slug = self.build_route_slug(page=page)

        frontend_url = template.format(
            page_id=page.pk,
            slug_name=page.slug,
            slug=route_slug,
            token=token,
        )
        frontend_url = self._canonicalise_preview_url(
            raw_url=frontend_url,
            slug=route_slug,
            token=token,
            page_id=page.pk,
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
