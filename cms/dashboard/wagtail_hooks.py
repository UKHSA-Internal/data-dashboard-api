from typing import List

from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" type="text/css" href="{}">', static("css/theme.css")
    )


ADDITIONAL_CUSTOM_ICONS: List[str] = [
    "icons/chart_plot.svg",
    "icons/chart_card.svg",
    "icons/standalone_chart.svg",
    "icons/headline_number.svg",
    "icons/number.svg",
    "icons/trend_down.svg",
    "icons/text.svg",
]


@hooks.register("register_icons")
def register_icons(icons: List[str]):
    """Registers additional svg icons used for the custom content blocks

    Args:
        icons: List of native svg filename icons

    Returns:
        List[str]: The list of native
            and additional custom svg icon filenames

    """
    return icons + ADDITIONAL_CUSTOM_ICONS
