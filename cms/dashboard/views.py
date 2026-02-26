from datetime import timedelta

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
        # should include placeholders for `{page_id}` and `{token}`. A default
        # value is provided to preserve previous behaviour.
        # See docs/environment_variables.md for PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE format.
        template = getattr(
            settings,
            "PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE",
            "http://localhost:3000/preview?page_id={page_id}&draft=true&t={token}",
        )

        frontend_url = template.format(page_id=page.pk, token=token)

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
