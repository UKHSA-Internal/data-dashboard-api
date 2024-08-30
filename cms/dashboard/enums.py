from enum import Enum

DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH = 10


class RelatedLinksLayoutEnum(Enum):
    Sidebar = "Sidebar"
    Footer = "Footer"

    @classmethod
    def choices(cls) -> tuple[tuple[str, str]]:
        return tuple(
            (layout_option.value, layout_option.value) for layout_option in cls
        )
