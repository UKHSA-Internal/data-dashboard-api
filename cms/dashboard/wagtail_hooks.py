from django.core.handlers.wsgi import WSGIRequest
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString
from draftjs_exporter.dom import DOM
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.site_summary import PagesSummaryItem, SummaryItem
from wagtail.models import Page
from wagtail.whitelist import check_url


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


@hooks.register("register_rich_text_features", order=1)
def register_link_props(features):
    rule = features.converter_rules_by_converter["contentstate"]["link"]
    rule["to_database_format"]["entity_decorators"]["LINK"] = link_entity_with_href
    features.register_converter_rule("contentstate", "link", rule)
