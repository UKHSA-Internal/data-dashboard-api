from collections.abc import Callable
from dataclasses import dataclass

from django import forms
from wagtail.admin.forms import WagtailAdminPageForm

from cms.dynamic_content import help_texts
from cms.metrics_interface.field_choices_callables import get_all_theme_names_and_ids


@dataclass
class NonPublicPageAdminField:
    """
    Class encapsulating the details about the non-public page fields which require dropdowns and other customisations.
    """

    # the name of the actual field on the non-public page (i.e. NonPublicPage)
    name: str
    # the label to display with the field
    label: str
    # the default choice for the dropdown
    choice_default: str
    # a callable which can be used to populate the Select widget's choices
    choice_callable: Callable | None = None

    def create_form_field(self) -> forms.CharField:
        choices = [("", self.choice_default)]

        if self.choice_callable is not None:
            choices.extend(self.choice_callable())

        return forms.CharField(
            required=False,
            label=self.label,
            widget=forms.Select(choices=choices),
            help_text=help_texts.NON_PUBLIC_PAGE_REQUIRED,
        )


# create fields to be used by the NonPublicPageAdminForm below
THEME_FIELD = NonPublicPageAdminField(
    name="page_theme",
    label="Theme",
    choice_default="----------",
    choice_callable=get_all_theme_names_and_ids,
)
SUB_THEME_FIELD = NonPublicPageAdminField(
    name="page_sub_theme",
    label="Sub-theme",
    choice_default="Select theme first",
)
TOPIC_FIELD = NonPublicPageAdminField(
    name="page_topic",
    label="Topic",
    choice_default="Select sub-theme first",
)


class NonPublicPageAdminForm(WagtailAdminPageForm):
    """
    Admin form class which we use to customise the theme/sub-theme/topic non-public page fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the fields
        for field in [THEME_FIELD, SUB_THEME_FIELD, TOPIC_FIELD]:
            self.fields[field.name] = field.create_form_field()

        # if there are already values, initialise further
        if self.instance and self.instance.pk:
            self._initialize_dependent_fields()

    def _initialize_dependent_fields(self):
        """
        Initialize choices for cascading dependent fields.
        """
        for field in [SUB_THEME_FIELD, TOPIC_FIELD]:
            value = getattr(self.instance, field.name, None)
            if value:
                choices = self._get_field_choices(value, field.choice_default)
                self.fields[field.name].widget.choices = choices

    @staticmethod
    def _get_field_choices(value, placeholder):
        """
        Generate choices list based on field value.
        """
        return [("", placeholder), (value, f"Loading... (ID: {value})")]

    class Media:
        js = ["js/toggle_available_fields_on_is_public.js"]
