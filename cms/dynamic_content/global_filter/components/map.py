from wagtail import blocks

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts

from .common import FilterLinkedComponent


class FilterLinkedMap(FilterLinkedComponent):
    about = blocks.RichTextBlock(
        required=False,
        default="",
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.OPTIONAL_MAP_ABOUT_FIELD,
    )

    class Meta:
        icon = "site"
