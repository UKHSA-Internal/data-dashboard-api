from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.snippets.models import register_snippet

from cms.snippets.managers.menu import MenuManager
from cms.snippets.models.menu_builder import help_texts
from cms.snippets.models.menu_builder.dynamic_content import ALLOWABLE_BODY_CONTENT


class MultipleMenusActiveError(ValidationError):
    def __init__(self):
        message = "There can only be 1 currently active `Menu`. Deactivate the first one before commencing."
        super().__init__(message)


@register_snippet
class Menu(models.Model):
    internal_label = models.TextField(help_text=help_texts.MENU_INTERNAL_LABEL)
    is_active = models.BooleanField(default=False, help_text=help_texts.MENU_IS_ACTIVE)
    body = ALLOWABLE_BODY_CONTENT

    panels = [
        FieldPanel("internal_label"),
        FieldPanel("is_active"),
        FieldPanel("body"),
    ]

    objects = MenuManager()

    def __str__(self) -> str:
        prefix = "Active" if self.is_active else "Inactive"
        return f"({prefix}) - {self.internal_label}"

    def clean(self) -> None:
        super().clean()
        self._raise_error_if_trying_to_enable_multiple_menus()

    def _raise_error_if_trying_to_enable_multiple_menus(self) -> None:
        has_existing_active_menu: bool = MenuManager.objects.has_active_menu()
        if has_existing_active_menu and self.is_active:
            raise MultipleMenusActiveError
