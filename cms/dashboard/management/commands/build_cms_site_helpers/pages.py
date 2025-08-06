import json
import logging
from collections.abc import Callable

from wagtail.models import Page

from cms.common.models import CommonPage, CommonPageRelatedLink
from cms.composite.models import CompositePage, CompositeRelatedLink
from cms.dashboard.management.commands.build_cms_site_helpers.index_pages import (
    create_cover_index_page_body,
    create_respiratory_viruses_index_page_body,
)
from cms.dashboard.management.commands.build_cms_site_helpers.landing_page import (
    create_landing_page_body_wih_page_links,
)
from cms.forms.models import FormField, FormPage
from cms.home.models import LandingPage
from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_internal_button_snippet,
)
from cms.topic.models import TopicPage, TopicPageRelatedLink
from cms.whats_new.models import Badge, WhatsNewChildEntry, WhatsNewParentPage
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

logger = logging.getLogger(__name__)

FILE_PATH = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/"


def open_example_page_response(*, page_name: str):
    path = f"{FILE_PATH}{page_name}.json"
    with open(path, "rb") as f:
        return json.load(f)


def _create_related_links(*, related_link_class, response_data, page) -> None:
    for related_link_response_data in response_data["related_links"]:
        related_link_model = related_link_class(
            page=page,
            title=related_link_response_data["title"],
            url=related_link_response_data["url"],
            body=related_link_response_data["body"],
        )
        related_link_model.save()


def _add_page_to_parent(*, page: Page, parent_page: Page) -> None:
    page = parent_page.add_child(instance=page)
    page.save_revision().publish()


def create_landing_page(*, parent_page: Page) -> LandingPage:
    data = open_example_page_response(page_name="landing_page")

    landing_page_body = create_landing_page_body_wih_page_links()

    page = LandingPage(
        title=data["title"],
        sub_title=data["sub_title"],
        body=landing_page_body,
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    return page


def _create_index_page(
    *, page_data: dict, parent_page: Page, create_index_page_body_func: Callable
) -> CompositePage:
    index_page_body: list[dict] = create_index_page_body_func()

    page = CompositePage(
        title=page_data["title"],
        page_description=page_data["page_description"],
        body=index_page_body,
        slug=page_data["meta"]["slug"],
        seo_title=page_data["meta"]["seo_title"],
        search_description=page_data["meta"]["search_description"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    return page


def create_respiratory_viruses_index_page(*, name: str, parent_page: Page):
    page_data = open_example_page_response(page_name=name)

    return _create_index_page(
        page_data=page_data,
        parent_page=parent_page,
        create_index_page_body_func=create_respiratory_viruses_index_page_body,
    )


def create_cover_index_page(*, name: str, parent_page: Page) -> CompositePage:
    page_data = open_example_page_response(page_name=name)

    page = _create_index_page(
        page_data=page_data,
        parent_page=parent_page,
        create_index_page_body_func=create_cover_index_page_body,
    )

    _create_related_links(
        related_link_class=CompositeRelatedLink,
        response_data=page_data,
        page=page,
    )

    return page


def create_topic_page(*, name: str, parent_page: Page) -> TopicPage:
    data = open_example_page_response(page_name=name)

    page = TopicPage(
        body=data["body"],
        title=data["title"],
        page_description=data["page_description"],
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=TopicPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def create_common_page(*, name: str, parent_page: Page) -> CommonPage:
    data = open_example_page_response(page_name=name)

    page = CommonPage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=CommonPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _remove_comment_from_body(*, body: dict[list[dict]]) -> list[dict]:
    return [item for item in body if "_comment" not in item]


def _get_or_create_button_id() -> int:
    internal_button_snippet = get_or_create_download_button_internal_button_snippet()
    return internal_button_snippet.id


def _add_download_button_to_composite_body(
    *, body: dict[list[dict]]
) -> dict[list[dict]]:
    body.append(
        {
            "type": "internal_button",
            "value": _get_or_create_button_id(),
            "id": "1431bc99-d4f9-4c80-880b-e96c5ad098db",
        }
    )
    return body


def create_bulk_downloads_page(*, name: str, parent_page: Page) -> CompositePage:
    data = open_example_page_response(page_name=name)

    body = _remove_comment_from_body(body=data["body"])
    composite_body = _add_download_button_to_composite_body(body=body)

    page = CompositePage(
        body=composite_body,
        title=data["title"],
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
    )

    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=CompositeRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def create_composite_page(*, name: str, parent_page: Page) -> CompositePage:
    data = open_example_page_response(page_name=name)

    page = CompositePage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
    )

    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=CompositeRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def create_whats_new_parent_page(*, name: str, parent_page: Page) -> WhatsNewParentPage:
    data = open_example_page_response(page_name=name)

    page = WhatsNewParentPage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    return page


def create_whats_new_child_entry(*, name: str, parent_page: Page) -> WhatsNewChildEntry:
    data = open_example_page_response(page_name=name)

    badge = Badge(text=data["badge"]["text"], colour=data["badge"]["colour"])
    badge.save()

    entry = WhatsNewChildEntry(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        additional_details=data["additional_details"],
        badge=badge,
    )
    _add_page_to_parent(page=entry, parent_page=parent_page)

    return entry


def _create_form_fields(*, form_field_class, response_data: dict, page: Page) -> None:
    for form_field_data in response_data["form_fields"]:
        form_field_model = form_field_class(
            page=page,
            clean_name=form_field_data["clean_name"],
            label=form_field_data["label"],
            field_type=form_field_data["field_type"],
            help_text=form_field_data["help_text"],
            required=form_field_data["required"],
            choices=form_field_data["choices"],
            default_value=form_field_data["default_value"],
        )
        form_field_model.save()


def create_feedback_page(*, name: str, parent_page: Page) -> FormPage:
    data = open_example_page_response(page_name=name)

    page = FormPage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        confirmation_slug=data["confirmation_slug"],
        confirmation_panel_title=data["confirmation_panel_title"],
        confirmation_panel_text=data["confirmation_panel_text"],
        confirmation_body=data["confirmation_body"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_form_fields(
        form_field_class=FormField,
        response_data=data,
        page=page,
    )

    return page
