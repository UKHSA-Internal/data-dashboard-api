from django.db import models
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from cms.dynamic_content import help_texts, elements
from cms.dynamic_content.components import (
    HeadlineNumberComponent,
    PercentageNumberComponent,
    TrendNumberComponent,
)

MINIMUM_ROWS_NUMBER_BLOCK_COUNT: int = 1
MAXIMUM_ROWS_NUMBER_BLOCK_COUNT: int = 2
METRIC_NUMBER_BLOCK_DATE_PREFIX_DEFAULT_TEXT = "Up to"


class HeadlineNumberBlockTypes(blocks.StreamBlock):
    headline_number = HeadlineNumberComponent(help_text=help_texts.HEADLINE_BLOCK_FIELD)
    trend_number = TrendNumberComponent(help_text=help_texts.TREND_BLOCK_FIELD)
    percentage_number = PercentageNumberComponent(
        help_text=help_texts.PERCENTAGE_BLOCK_FIELD
    )

    class Meta:
        icon = "bars"


class MetricNumberBlockTypes(blocks.StructBlock):
    title = blocks.TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    date_prefix = blocks.TextBlock(
        required=True,
        default=METRIC_NUMBER_BLOCK_DATE_PREFIX_DEFAULT_TEXT,
        help_text=help_texts.HEADLINE_DATE_PREFIX,
    )
    rows = HeadlineNumberBlockTypes(
        required=True,
        min_num=MINIMUM_ROWS_NUMBER_BLOCK_COUNT,
        max_num=MAXIMUM_ROWS_NUMBER_BLOCK_COUNT,
        help_text=help_texts.NUMBERS_ROW_FIELD.format(MAXIMUM_ROWS_NUMBER_BLOCK_COUNT),
    )

    class Meta:
        icon = "table"


class MetricNumberBlock(blocks.StreamBlock):
    column = MetricNumberBlockTypes()


class ProgrammingLanguages(models.TextChoices):
    JAVASCRIPT = "Javascript"
    PYTHON = "Python"
    TEXT = "Text"
    JSON = "JSON"

    @classmethod
    def get_programming_languages(cls) -> tuple[tuple[str, str]]:
        return tuple((language.value, language.value) for language in cls)


class CodeSnippet(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        choices=ProgrammingLanguages.get_programming_languages,
        default=ProgrammingLanguages.JAVASCRIPT.value,
    )
    code = blocks.TextBlock(
        form_classname="codeblock_monospace",
        help_text=help_texts.CODE_SNIPPET,
    )


class CodeBlock(blocks.StreamBlock):
    code_snippet = CodeSnippet()


class ButtonChooserBlock(SnippetChooserBlock):
    @classmethod
    def get_api_representation(cls, value, context=None) -> dict | None:
        if value:
            return {
                "text": value.text,
                "loading_text": value.loading_text,
                "endpoint": value.endpoint,
                "method": value.method,
                "button_type": value.button_type,
            }
        return None


class InternalButtonChooserBlock(SnippetChooserBlock):
    @classmethod
    def get_api_representation(cls, value, context=None) -> dict | None:
        if value:
            return {
                "text": value.text,
                "button_type": value.button_type,
                "endpoint": value.endpoint,
                "method": value.method,
            }
        return None


class ExternalButtonChooserBlock(SnippetChooserBlock):
    @classmethod
    def get_api_representation(cls, value, context=None) -> dict | None:
        if value:
            return {
                "text": value.text,
                "url": value.url,
                "button_type": value.button_type,
                "icon": value.icon,
            }
        return None


class WhaButtonChooserBlock(SnippetChooserBlock):
    @classmethod
    def get_api_representation(cls, value, context=None) -> dict | None:
        if value:
            return {
                "text": value.text,
                "button_type": value.button_type,
                "geography_code": value.geography_code,
            }
        return None


class PageLinkChooserBlock(blocks.PageChooserBlock):
    @classmethod
    def get_api_representation(cls, value, context=None) -> str | None:
        if value:
            return value.full_url

        return None


class PageLink(blocks.StructBlock):
    title = blocks.CharBlock(
        required=True,
        help_text=help_texts.PAGE_LINK_TITLE,
    )
    sub_title = blocks.CharBlock(
        required=False,
        help_text=help_texts.PAGE_LINK_SUB_TITLE,
    )
    page = PageLinkChooserBlock(target_model=["topic.TopicPage"])


class InternalPageLinks(blocks.StreamBlock):
    page_link = PageLink()

    class Meta:
        icon = "link"


from typing import Dict, Any
from django import forms
from wagtail import blocks
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock

from typing import Dict, Any
from django import forms
from wagtail import blocks
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock


class ParameterizedColumnBlock(blocks.StructBlock):
    """
    A custom block for creating columns with fixed base parameters
    and cell-specific overrides.
    """
    # First cell block with all base parameters
    base_params = blocks.StructBlock([
        ('metric', blocks.ChoiceBlock(
            choices=[
                ('ABC', 'Metric ABC'),
                ('XYZ', 'Metric XYZ'),
                # Add your actual metrics here
            ],
            required=True
        )),
        ('topic', blocks.ChoiceBlock(
            choices=[
                ('DEF', 'Topic DEF'),
                ('GHI', 'Topic GHI'),
                # Add your actual topics here
            ],
            required=True
        )),
        ('age', blocks.ChoiceBlock(
            choices=[
                ('0-4', '0-4 years'),
                ('5-14', '5-14 years'),
                ('15-24', '15-24 years'),
                # Add your age groups
            ],
            required=True
        )),
        ('stratum', blocks.ChoiceBlock(
            choices=[
                ('default', 'Default Stratum'),
                # Add your strata options
            ],
            required=True
        )),
        ('geography', blocks.ChoiceBlock(
            choices=[
                ('Wales', 'Wales'),
                ('Scotland', 'Scotland'),
                ('England', 'England'),
                # Add other geography options
            ],
            required=True
        ))
    ], label="Base Parameters for Column")

    # Subsequent cell override block
    override = blocks.StructBlock([
        ('parameter', blocks.ChoiceBlock(
            choices=[
                ('metric', 'Metric'),
                ('topic', 'Topic'),
                ('age', 'Age'),
                ('stratum', 'Stratum'),
                ('geography', 'Geography'),
            ],
            required=True,
            help_text="Select which parameter to override"
        )),
        ('value', blocks.ChoiceBlock(
            choices=[],  # This will be dynamically populated
            required=True,
            help_text="Select the new value for the overridden parameter"
        ))
    ], label="Cell-Specific Override", required=False)

    def get_dynamic_choices(self, parameter):
        """
        Dynamically populate choices based on the selected parameter.

        Args:
            parameter (str): The parameter to get choices for

        Returns:
            list: A list of tuples containing choices
        """
        choices_map = {
            'metric': [
                ('ABC', 'Metric ABC'),
                ('XYZ', 'Metric XYZ'),
                # Add your actual metrics here
            ],
            'topic': [
                ('DEF', 'Topic DEF'),
                ('GHI', 'Topic GHI'),
                # Add your actual topics here
            ],
            'age': [
                ('0-4', '0-4 years'),
                ('5-14', '5-14 years'),
                ('15-24', '15-24 years'),
                # Add your age groups
            ],
            'stratum': [
                ('default', 'Default Stratum'),
                # Add your strata options
            ],
            'geography': [
                ('Wales', 'Wales'),
                ('Scotland', 'Scotland'),
                ('England', 'England'),
                # Add other geography options
            ]
        }
        return choices_map.get(parameter, [])

    def get_form_class(self):
        """
        Customize the form to dynamically update override value choices.
        """

        class DynamicParameterForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Dynamically set choices for override value
                override_parameter = self.initial.get('override', {}).get('parameter')
                if override_parameter:
                    self.fields['override']['value'].choices = self.block.get_dynamic_choices(override_parameter)

        return DynamicParameterForm


class CustomTableBlock(blocks.StreamBlock):
    """
    Custom table block with the parameterized column type.
    """
    table = TypedTableBlock([
        ('text', blocks.CharBlock()),  # Original text column type
        ('parameterized', ParameterizedColumnBlock()),  # New custom column type
    ])

class CustomTableBlock(blocks.StreamBlock):
    """
    Custom table block with the parameterized column type.
    """
    table = TypedTableBlock([
        ('text', blocks.CharBlock()),  # Original text column type
        ('parameterized', ParameterizedColumnBlock()),  # New custom column type
    ])




from wagtail.contrib.typed_table_block.blocks import TypedTableBlock
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class CustomTableBlock(blocks.StreamBlock):
    table = TypedTableBlock([
        ('text', blocks.CharBlock()),
        ('data', ParameterizedColumnBlock())
    ])
