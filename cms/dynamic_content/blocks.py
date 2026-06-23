from django.core.exceptions import ValidationError
from django.db import models
from wagtail import blocks
from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    PageChooserBlock,
    StreamBlock,
    StructBlock,
    StructValue,
    TextBlock,
    URLBlock,
)
from wagtail.snippets.blocks import SnippetChooserBlock

from cms.dynamic_content import help_texts
from cms.dynamic_content.components import (
    HeadlineNumberComponent,
    PercentageNumberComponent,
    TrendNumberComponent,
)
from validation.url import validate_https_scheme

MINIMUM_ROWS_NUMBER_BLOCK_COUNT: int = 1
MAXIMUM_ROWS_NUMBER_BLOCK_COUNT: int = 2

POPULAR_TOPICS_BOTTOM_RIGHT_COLUMN_COUNT: int = 2
POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT: int = 2

METRIC_NUMBER_BLOCK_DATE_PREFIX_DEFAULT_TEXT = "Up to"



def check_permissions(user_permissions, theme_id, sub_theme_id, topic_id) -> bool:
    if not isinstance(user_permissions, list):
        return False

    for permission in user_permissions:
        permission_theme_id = permission.get("theme", {}).get("id")
        permission_sub_theme_id = permission.get("sub_theme", {}).get("id")
        permission_topic_id = permission.get("topic", {}).get("id")

        if permission_theme_id == "-1":
            return True

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == "-1"
        ):
            return True

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == sub_theme_id
            and (permission_topic_id in {"-1", topic_id})
        ):
            return True

    return False



class HeadlineNumberBlockTypes(StreamBlock):
    headline_number = HeadlineNumberComponent(help_text=help_texts.HEADLINE_BLOCK_FIELD)
    trend_number = TrendNumberComponent(help_text=help_texts.TREND_BLOCK_FIELD)
    percentage_number = PercentageNumberComponent(
        help_text=help_texts.PERCENTAGE_BLOCK_FIELD
    )

    class Meta:
        icon = "bars"


class MetricNumberBlockTypes(StructBlock):
    title = TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    date_prefix = TextBlock(
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


class PopularTopicsHeadlineNumberBlockTypes(StreamBlock):
    headline_number = HeadlineNumberComponent(help_text=help_texts.HEADLINE_BLOCK_FIELD)
    trend_number = TrendNumberComponent(help_text=help_texts.TREND_BLOCK_FIELD)

    class Meta:
        icon = "bars"


class PageLinkChooserBlock(PageChooserBlock):
    @classmethod
    def get_api_representation(cls, value, context=None) -> str | None:
        if value:
            return value.full_url
        return None


class PopularTopicsMetricNumberBlockTypes(StructBlock):
    title = TextBlock(required=True, help_text=help_texts.TITLE_FIELD)
    date_prefix = TextBlock(
        required=True,
        default=METRIC_NUMBER_BLOCK_DATE_PREFIX_DEFAULT_TEXT,
        help_text=help_texts.HEADLINE_DATE_PREFIX,
    )
    topic_page = PageLinkChooserBlock(
        page_type="topic.TopicPage",
        required=True,
        help_text=help_texts.TOPIC_PAGE_FIELD,
    )
    headline_metrics = PopularTopicsHeadlineNumberBlockTypes(
        required=True,
        min_num=POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT,
        max_num=POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT,
        help_text=help_texts.POPULAR_TOPICS_METRIC_CARDS.format(
            POPULAR_TOPICS_HEADLINE_NUMBER_BLOCK_COUNT
        ),
    )

    class Meta:
        icon = "table"


class PopularTopicsRightColumnBottomRowBlockTypes(StreamBlock):
    headline_metric_card = PopularTopicsMetricNumberBlockTypes(
        required=True,
        min_num=POPULAR_TOPICS_BOTTOM_RIGHT_COLUMN_COUNT,
        max_num=POPULAR_TOPICS_BOTTOM_RIGHT_COLUMN_COUNT,
        help_text=help_texts.POPULAR_TOPICS_HEADLINE_METRIC_CARDS,
    )

    class Meta:
        icon = "table"


class MetricNumberBlock(StreamBlock):
    column = MetricNumberBlockTypes()


class ProgrammingLanguages(models.TextChoices):
    JAVASCRIPT = "Javascript"
    PYTHON = "Python"
    R = "R"
    TEXT = "Text"
    JSON = "JSON"

    @classmethod
    def get_programming_languages(cls) -> tuple[tuple[str, str]]:
        return tuple((language.value, language.value) for language in cls)


class CodeSnippet(StructBlock):
    language = ChoiceBlock(
        choices=ProgrammingLanguages.get_programming_languages,
        default=ProgrammingLanguages.JAVASCRIPT.value,
    )
    code = TextBlock(
        form_classname="codeblock_monospace",
        help_text=help_texts.CODE_SNIPPET,
    )


class CodeBlock(StreamBlock):
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
            }
        return None


class PageLink(StructBlock):
    title = CharBlock(
        required=True,
        help_text=help_texts.PAGE_LINK_TITLE,
    )
    sub_title = CharBlock(
        required=False,
        help_text=help_texts.PAGE_LINK_SUB_TITLE,
    )
    page = PageLinkChooserBlock(target_model=["topic.TopicPage"])
    
    
    def get_api_representation(self, value, context=None):
        page = value.get("page")
        if not page:
            return None

        request = context.get("request") if context else None
        user = getattr(request, "user", None)
        user_permissions = getattr(user, "permission_sets", None)
        full_user_permissions = user_permissions.permission_sets["permission_sets"]

        topic_page_details = value.specific
        
        if getattr(topic_page_details, "is_public", False):
            page_theme = getattr(topic_page_details, "theme", None)
            page_sub_theme = getattr(topic_page_details, "sub_theme", None)
            page_topic = getattr(topic_page_details, "topic", None)
            print(f"🦄 theme: {page_theme}")
            print(f"🦄🦄 full_user_permissions: {full_user_permissions}")
            
            if not check_permissions(
                full_user_permissions,
                page_theme,
                page_sub_theme, 
                page_topic
            ):
                return None

        return {
            "title": value.get("title"),
            "url": topic_page_details.full_url,
        }



class InternalPageLinks(StreamBlock):
    page_link = PageLink()
    
    
    def get_api_representation(self, value, context=None):
        data = super().get_api_representation(value, context=context)

        # Remove filtered-out items (None)
        return [item for item in data if item is not None]

    
    class Meta:
        icon = "link"


class RelatedLink(StructBlock):
    link_display_text = CharBlock(required=True, help_text=help_texts.RELATED_LINK_TEXT)
    link = CharBlock(required=True, help_text=help_texts.RELATED_LINK_URL)


class RelatedLinkBlock(StreamBlock):
    related_link = RelatedLink()


class SourceLinkBlock(StructBlock):
    """Source link supporting internal (page) or external (URL) links."""

    link_display_text = CharBlock(
        required=False,
        help_text=help_texts.SOURCE_LINK_TEXT,
    )
    page = PageLinkChooserBlock(
        target_model=["topic.TopicPage"],
        required=False,
        help_text=help_texts.SOURCE_LINK_PAGE,
    )
    external_url = URLBlock(
        required=False,
        help_text=help_texts.SOURCE_LINK_URL,
        validators=[validate_https_scheme],
    )

    def clean(self, value: StructValue):
        self._validate_only_one_of_page_or_external_url(value=value)
        return super().clean(value=value)

    @classmethod
    def _validate_only_one_of_page_or_external_url(cls, *, value: StructValue) -> None:
        """Validate that only one of the page or external_url fields is set if provided."""
        page = value.get("page")
        external_url = value.get("external_url")

        if page and external_url:
            error_message = "Use either page OR external_url, not both."
            raise ValidationError(error_message)


class SectionFooterLink(StructBlock):
    badge_label = CharBlock(
        help_text=help_texts.SECTION_FOOTER_BADGE_LABEL, required=True
    )
    text = CharBlock(help_text=help_texts.SECTION_FOOTER_LINK_TEXT, required=True)
    link = SourceLinkBlock(help_text=help_texts.SECTION_FOOTER_LINK, required=True)

    class Meta:
        icon = "link"


class HealthTopicSectionLink(blocks.StructBlock):
    heading = blocks.TextBlock(help_text=help_texts.HEADING_BLOCK, required=True)
    page = PageLinkChooserBlock(
        page_type=["topics_list.TopicsListPage"],
        required=True,
        help_text=help_texts.TOPIC_PAGE_FIELD,
    )

    class Meta:
        icon = "link"

    @classmethod
    def get_api_representation(cls, value, context=None) -> dict | None:
        if value:
            page = value.get("page")

            return {
                "heading": value["heading"],
                "page": page.id if page else None,
            }
        return None
