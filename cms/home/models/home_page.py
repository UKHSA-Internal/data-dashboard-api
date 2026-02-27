from wagtail.models import Page


class UKHSARootPage(Page):
    custom_preview_enabled: bool = False

    max_count = 1
