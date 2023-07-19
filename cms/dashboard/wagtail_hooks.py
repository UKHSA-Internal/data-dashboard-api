from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString
from wagtail import hooks
from wagtail.admin.site_summary import PagesSummaryItem
from wagtail.documents.wagtail_hooks import DocumentsMenuItem


@hooks.register("insert_global_admin_css")
def global_admin_css() -> SafeString:
    return format_html(
        '<link rel="stylesheet" type="text/css" href="{}">', static("css/theme.css")
    )


@hooks.register("construct_main_menu")
def hide_default_menu_items(request, menu_items: list[DocumentsMenuItem]) -> None:
    """update menu items to remove `Documents` and `Images`

    Args:
        request: Request object provided by wagtail
        menu_items: a list of objects containing menu items for the admin page.

    Return:
        None
    """
    menu_items[:] = [
        item for item in menu_items if item.name != "images" if item.name != "documents"
    ]


@hooks.register("construct_homepage_summary_items", order=1)
def update_summary_items(request, summary_items: list[object]) -> list[object]:
    """Updates the homepage summary items to remove default items `Documents` and `Images`

    Args:
        request: Request object provided by wagtail
        summary_items: a list of objects providing the summary items to be displayed.

    returns:
        summary_items: an updated list of objects for display on the summary items panel.
    """
    summary_items[:] = [PagesSummaryItem(request)]
    return summary_items


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
