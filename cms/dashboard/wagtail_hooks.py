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

from cms.dashboard.views import PreviewToFrontendRedirectView


PagePreviewEnabled: dict[str, bool] = {
    "UKHSARootPage": False,
    "LandingPage": True,
    "TopicPage": True,
    "CommonPage": False,
    "CompositePage": True,
    "FormPage": True,
    "MetricsDocumentationParentPage": True,
    "MetricsDocumentationChildEntry": True,
    "WhatsNewParentPage": True,
    "WhatsNewChildEntry": True,
}


def _is_preview_enabled_page(page: Page) -> bool:
    for page_class in page.__class__.mro():
        page_type_name = page_class.__name__
        if page_type_name in PagePreviewEnabled:
            return PagePreviewEnabled[page_type_name]

    try:
        specific_class = page.specific_class
    except RuntimeError:
        specific_class = None

    if specific_class:
        return PagePreviewEnabled.get(specific_class.__name__, False)

    return False


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
def frontend_preview_button(page, user, next_url, view_name):
    """Add a preview button to the page header that redirects to the frontend.

    The admin view will create a signed token and then redirect to the
    frontend. We reverse the admin URL by name; if reversing fails we fall
    back to a direct frontend URL.

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

    if not _is_preview_enabled_page(page):
        return []

    try:
        admin_url = reverse("cms_preview_to_frontend", args=[page.pk])
    except NoReverseMatch:
        template = getattr(
            settings,
            "FRONTEND_PREVIEW_URL_TEMPLATE",
            "http://localhost:3000/preview?page_id={page_id}&draft=true",
        )
        admin_url = template.format(page_id=page.pk)

    return [Button("Preview", url=admin_url, priority=10)]


def link_entity_with_href(props: dict):
    link_props = _build_link_props(props=props)
    return DOM.create_element("a", link_props, props["children"])


def _build_link_props(props: dict) -> dict[str, str | int]:
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
    try:
        page = Page.objects.get(id=page_id).specific
    except Page.DoesNotExist:
        return ""
    return page.full_url


@hooks.register("register_admin_urls")
def register_admin_urls():
    """Register admin URLs for CMS dashboard views.

    We register an admin redirect endpoint 
    (`/admin/preview-to-frontend/<pk>/`) that signs a short-lived 
    preview token and redirects the user to the external frontend. 
    The redirect logic is implemented in `cms.dashboard.views`.
    """
    return [
        re_path(
            r"^preview-to-frontend/(?P<pk>[0-9]+)/$",
            PreviewToFrontendRedirectView.as_view(),
            name="cms_preview_to_frontend",
        ),
    ]


@hooks.register("register_rich_text_features", order=1)
def register_link_props(features):
    rule = features.converter_rules_by_converter["contentstate"]["link"]
    rule["to_database_format"]["entity_decorators"]["LINK"] = link_entity_with_href
    features.register_converter_rule("contentstate", "link", rule)


@hooks.register("construct_page_action_menu")
def add_frontend_preview_action(menu_items, request, context):
    """Insert a top-level Preview action that redirects to the frontend.

    We add this to the page action menu so it appears as a primary action in
    the page editor header (rather than being buried in a dropdown). If the
    page has no primary key (create view) we skip adding it.

    Args:
        menu_items: List of menu items to modify in place.
        request: The current HTTP request.
        context: Context dictionary containing the page being edited.

    Note:
        This method is conservative and silently returns on any exception to
        avoid breaking the editor UI.
    """
    page = context.get("page")
    if not page or not getattr(page, "pk", None):
        return

    if not _is_preview_enabled_page(page):
        return

    try:
        admin_url = reverse("cms_preview_to_frontend", args=[page.pk])
    except (NoReverseMatch, RuntimeError):
        return

    class FrontendPreviewAction(ActionMenuItem):
        """ActionMenuItem for frontend preview with external link icon.

        Attributes:
            label: Display text for the menu item.
            name: Unique identifier for the action.
            icon_name: Wagtail icon name to display.
        """

        label = "Preview"
        name = "action-preview"
        icon_name = "link-external"

        def __init__(self, url: str, order: int = None):
            super().__init__(order=order)
            self._url = url

        def get_url(self, parent_context):
            """Return the preview URL.

            Args:
                parent_context: Context from parent menu.

            Returns:
                The preview redirect URL.
            """
            return self._url

    try:
        preview_item = FrontendPreviewAction(admin_url, order=0)
        menu_items.insert(0, preview_item)
    except RuntimeError:
        return
