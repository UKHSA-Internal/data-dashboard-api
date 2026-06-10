import logging
import re
from typing import Any

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.templatetags.static import static
from django.urls import NoReverseMatch, re_path, reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from draftjs_exporter.dom import DOM
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem
from wagtail.admin.menu import MenuItem
from wagtail.admin.site_summary import PagesSummaryItem, SummaryItem
from wagtail.admin.widgets import Button
from wagtail.models import Page
from wagtail.whitelist import check_url

from cms.dashboard.views import FrontendRedirectView

VIEW_LIVE_LABEL = "View Live"
PREVIEW_LABEL = "Preview"
ROUTES = {PREVIEW_LABEL: "preview", VIEW_LIVE_LABEL: "nocache"}
logger = logging.getLogger(__name__)


class FrontendRedirectAction(ActionMenuItem):
    """Primary action-menu item that links editors to the frontend preview flow."""

    name = "action-preview"
    icon_name = "preview"
    template_name = "wagtailadmin/pages/action_menu/frontend_preview.html"

    def __init__(self, url: str, label: str, order: int | None = None):
        """Store the target URL and label for the custom action item."""
        super().__init__(order=order)
        self._url = url
        self.label = label

    def get_url(self, parent_context):
        """Return the precomputed frontend URL for this action item."""
        return self._url


def _get_preview_button_label(page: Page) -> str | None:
    """Return the appropriate preview action label for the given page state."""
    if not page.custom_preview_enabled:
        return None

    has_draft = page.has_unpublished_changes
    has_live = page.live

    if has_draft:
        return PREVIEW_LABEL

    if has_live:
        return VIEW_LIVE_LABEL

    return None


def _build_frontend_redirect_url(page: Page, route: str) -> str | None:
    """Build the admin redirect URL used by the top-level View Live action."""
    try:
        return f"{reverse('redirect-to-frontend', args=[page.pk])}?route={route}"
    except NoReverseMatch as e:
        error_message = f"Could not reverse_lookup 'redirect-to-frontend'.  Has this url been registered correctly in register_admin_urls? {e}"
        logger.exception(error_message)
    return None


@hooks.register("insert_global_admin_css")
def global_admin_css() -> SafeString:
    return format_html(
        '<link rel="stylesheet" type="text/css" href="{}">', static("css/theme.css")
    )


@hooks.register("construct_main_menu")
def hide_default_menu_items(request: WSGIRequest, menu_items: list[MenuItem]) -> None:
    """Update menu items to remove `Documents` and `Images`

    Notes:
        menu_items has to be mutated as required by wagtail's hook, which is why we're not returning
        a new value.

    Args:
        request: Request object provided by wagtail
        menu_items: A list of objects containing menu items for the admin page.

    Returns:
        None

    """
    menu_items[:] = [
        item for item in menu_items if item.name != "images" if item.name != "documents"
    ]


@hooks.register("construct_homepage_summary_items", order=1)
def update_summary_items(
    request: WSGIRequest, summary_items: list[type[SummaryItem]]
) -> None:
    """Updates the homepage summary items to remove default items `Documents` and `Images`

    Notes:
        summary_items has to be mutated as required by wagtail's hook, which is why we're not returning
        a new value.

    Args:
        request: Request object provided by wagtail
        summary_items: A list of objects providing the summary items to be displayed.

    Returns:
        None

    """
    summary_items[:] = [PagesSummaryItem(request)]


ADDITIONAL_CUSTOM_ICONS: list[str] = [
    "icons/chart_row_card.svg",
    "icons/chart_plot.svg",
    "icons/chart_with_headline_and_trend_card.svg",
    "icons/standalone_chart.svg",
    "icons/headline_number.svg",
    "icons/number.svg",
    "icons/trend_down.svg",
    "icons/text.svg",
    "icons/percentage.svg",
    "icons/weather.svg",
    "icons/preview.svg",
    "icons/rocket.svg",
]


@hooks.register("register_icons")
def register_icons(icons: list[str]) -> list[str]:
    """Registers additional svg icons used for the custom content blocks

    Args:
        icons: List of native svg filename icons

    Returns:
        List[str]: The list of native
            and additional custom svg icon filenames

    """
    return icons + ADDITIONAL_CUSTOM_ICONS


@hooks.register("register_page_header_buttons")
def frontend_preview_button(
    page: Page,
    user: Any,
    next_url: str | None,
    view_name: str,
) -> list[Button]:
    """Add a preview button to the page header that redirects to the frontend.

    The admin view will create a signed token and then redirect to the
    frontend. We reverse the admin URL by name. If reversing fails, no
    preview button is rendered.

    Args:
        page: The page being edited.
        user: The current user.
        next_url: The next URL after action.
        view_name: The current view name (e.g., 'edit').

    Returns:
        List of Button instances for the page header, or empty list if not
        in edit view.
    """
    if view_name != "edit":
        return []

    # Hide preview and view live buttons if PAGE_PREVIEWS_ENABLED is False
    if not settings.PAGE_PREVIEWS_ENABLED:
        return []

    button_label = _get_preview_button_label(page=page)
    if button_label is None:
        return []

    url = _build_frontend_redirect_url(page=page, route=ROUTES[button_label])

    if url is None:
        return []

    return [
        Button(
            label=button_label,
            url=url,
            priority=10,
            attrs={"target": "_blank", "rel": "noopener noreferrer"},
        )
    ]


def link_entity_with_href(props: dict):
    """Render a rich-text link entity while preserving a resolved href value."""
    link_props = _build_link_props(props=props)
    return DOM.create_element("a", link_props, props["children"])


def _build_link_props(props: dict) -> dict[str, str | int]:
    """Build rich-text link attributes, resolving page links to hrefs when possible."""
    link_props = {}
    page_id = props.get("id")

    if page_id is not None:
        link_props["linktype"] = "page"
        link_props["id"] = page_id

        # This is the added functionality
        # on top of the original Wagtail implementation
        page_url = _get_page_url(page_id=page_id)
        link_props["href"] = page_url
    else:
        link_props["href"] = check_url(url_string=props.get("url"))

    return link_props


def _get_page_url(page_id: int) -> str:
    """Return the full URL for a linked page or an empty string if unavailable."""
    try:
        page = Page.objects.get(id=page_id).specific
    except Page.DoesNotExist:
        return ""
    return page.full_url


@hooks.register("register_admin_urls")
def register_admin_urls():
    """Register admin URLs for CMS dashboard views.

    We register an admin redirect endpoint
    (`/admin/redirect-to-frontend/<pk>/`) that signs a short-lived
    preview token and redirects the user to the external frontend.
    The redirect logic is implemented in `cms.dashboard.views`.
    """
    return [
        re_path(
            r"^redirect-to-frontend/(?P<pk>[0-9]+)/$",
            FrontendRedirectView.as_view(),
            name="redirect-to-frontend",
        )
    ]


@hooks.register("register_rich_text_features", order=1)
def register_link_props(features):
    """Extend Wagtail rich-text link conversion to include resolved href values."""
    rule = features.converter_rules_by_converter["contentstate"]["link"]
    rule["to_database_format"]["entity_decorators"]["LINK"] = link_entity_with_href
    features.register_converter_rule("contentstate", "link", rule)


@hooks.register("construct_page_action_menu")
def add_frontend_preview_action(
    menu_items: list[Any],
    request: WSGIRequest | None,
    context: dict[str, Any],
) -> None:
    """Insert a top-level Preview action that redirects to the frontend.

    We add this to the page action menu so it appears as a primary action in
    the page editor header (rather than being buried in a dropdown). If the
    page has no primary key (create view) we skip adding it.

    Args:
        menu_items: List of menu items to modify in place.
        request: The current HTTP request.
        context: Context dictionary containing the page being edited.

    Note:
        This method is conservative and returns early if inputs or settings are
        not suitable for showing a frontend preview action. Unexpected
        runtime errors are logged and ignored to avoid breaking the editor UI.
    """
    try:
        page = context.get("page")
        if not page or not getattr(page, "pk", None):
            logger.debug("Skipping frontend preview action: page missing or unsaved")
            return

        if not settings.PAGE_PREVIEWS_ENABLED:
            logger.debug(
                "Skipping frontend preview action: PAGE_PREVIEWS_ENABLED is False."
            )
            return

        button_label = _get_preview_button_label(page=page)
        if button_label is None:
            logger.debug(
                "Skipping frontend preview action: no preview/view-live label for page %s",
                page.pk,
            )
            return

        action_url = _build_frontend_redirect_url(page=page, route=ROUTES[button_label])

        if action_url:
            redirect_item = FrontendRedirectAction(
                url=action_url, label=button_label, order=0
            )
            menu_items.insert(0, redirect_item)
    except (AttributeError, TypeError, ValueError, LookupError, RuntimeError):
        logger.debug(
            "Failed to construct frontend preview action; editor UI will continue"
        )


def _replace_view_live_button_href(message_html: str, target_url: str) -> str:
    """Replace the first View live anchor href in a Wagtail flash message."""
    return re.sub(
        r'(<a\s+href=")([^"]*)(")([^>]*)(>\s*View live\s*</a>)',
        rf'\1{target_url}\3\4 target="_blank" rel="noreferrer"\5',
        message_html,
        count=1,
        flags=re.IGNORECASE,
    )


def _rewrite_view_live_button_in_messages(messages_list: list, live_url: str) -> bool:
    """Rewrite the first matching View live button in the supplied message list."""
    for message in reversed(messages_list):
        message_html = str(getattr(message, "message", ""))
        if "View live" not in message_html:
            continue

        updated_html = _replace_view_live_button_href(
            message_html=message_html,
            target_url=live_url,
        )
        if updated_html != message_html:
            # nosec B703 - updated_html is Wagtail's own flash message HTML with only
            # the href replaced by a settings-derived URL; no user input is interpolated.
            # There's no injection vector. Bandit simply can't infer that statically, hence the false positive.
            message.message = SafeString(updated_html)  # nosec B703
            return True

    return False


def _rewrite_post_publish_view_live_button_url(
    request: WSGIRequest, page: Page
) -> None:
    """Rewrite Wagtail's post-publish View live button to the frontend host."""
    if not settings.PAGE_PREVIEWS_ENABLED:
        return

    if not getattr(page, "live", False):
        return

    live_url = _build_frontend_redirect_url(page=page, route=ROUTES[VIEW_LIVE_LABEL])
    if not live_url:
        return

    storage = getattr(request, "_messages", None)
    if not storage:
        return

    for messages_attr in ("_queued_messages", "_loaded_messages"):
        messages_list = getattr(storage, messages_attr, None)
        if not messages_list:
            continue

        if _rewrite_view_live_button_in_messages(messages_list, live_url):
            return


@hooks.register("after_edit_page")
def rewrite_post_publish_view_live_button_after_edit(
    request: WSGIRequest,
    page: Page,
) -> None:
    """Apply frontend View live URL rewriting after editing a page."""
    _rewrite_post_publish_view_live_button_url(request=request, page=page)


@hooks.register("after_create_page")
def rewrite_post_publish_view_live_button_after_create(
    request: WSGIRequest,
    page: Page,
) -> None:
    """Apply frontend View live URL rewriting after creating a page."""
    _rewrite_post_publish_view_live_button_url(request=request, page=page)
