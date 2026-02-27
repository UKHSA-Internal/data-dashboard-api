import pytest
from wagtail.models import Page

from cms.acknowledgement.models import AcknowledgementPage
from cms.dashboard.management.commands import build_cms_site_helpers
from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)


class TestAcknowledgementPageManager:
    @pytest.mark.django_db
    def test_get_live_pages(self):
        """
        Given 2 `AcknowledgementPage` records of which only 1 is live
        When `get_live_pages()` is called from the `AcknowledgementPageManager`
        Then the correct `AcknowledgementPage` record is returned
        """
        # Given
        live_page = AcknowledgementPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            body="",
            live=True,
            seo_title="ABC",
            i_agree_checkbox="I agree",
            terms_of_service_link_text="Terms of service",
            terms_of_service_link="https://example.com/terms",
            disagree_button="I do not agree",
            agree_button="I agree",
        )
        unpublished_page = AcknowledgementPage.objects.create(
            path="def",
            depth=1,
            title="def",
            body="",
            live=False,
            seo_title="DEF",
            i_agree_checkbox="I agree",
            terms_of_service_link_text="Terms of service",
            terms_of_service_link="https://example.com/terms",
            disagree_button="I do not agree",
            agree_button="I agree",
        )

        # When
        retrieved_live_pages = AcknowledgementPage.objects.get_live_pages()

        # Then
        assert live_page in retrieved_live_pages
        assert unpublished_page not in retrieved_live_pages


class TestCreateAcknowledgementPage:
    @pytest.mark.django_db
    def test_create_acknowledgement_page_sets_expected_fields(self):
        """
        Given an example acknowledgement page response payload
        When `create_acknowledgement_page()` is called
        Then the expected content fields are set on the created page
        """
        # Given
        root_page = Page.get_first_root_node()
        expected_data = open_example_page_response(page_name="acknowledgement")

        # When
        page = build_cms_site_helpers.create_acknowledgement_page(
            name="acknowledgement", parent_page=root_page
        )

        # Then
        assert page.title == expected_data["title"]
        assert page.slug == expected_data["meta"]["slug"]
        assert page.seo_title == expected_data["meta"]["seo_title"]
        assert page.search_description == expected_data["meta"]["search_description"]
        assert page.body == expected_data.get("body", "")
        assert page.i_agree_checkbox == expected_data.get("i_agree_checkbox", "")
        assert page.terms_of_service_link_text == expected_data.get(
            "terms_of_service_link_text", ""
        )
        assert page.terms_of_service_link == expected_data.get(
            "terms_of_service_link", ""
        )
        assert page.disagree_button == expected_data.get("disagree_button", "")
        assert page.agree_button == expected_data.get("agree_button", "")

    @pytest.mark.django_db
    def test_create_acknowledgement_page_is_live_child_of_parent(self):
        """
        Given a root page
        When `create_acknowledgement_page()` is called
        Then the created page is published and attached to the parent page
        """
        # Given
        root_page = Page.get_first_root_node()

        # When
        page = build_cms_site_helpers.create_acknowledgement_page(
            name="acknowledgement", parent_page=root_page
        )
        page.refresh_from_db()

        # Then
        assert page.is_child_of(root_page)
        assert page.live
