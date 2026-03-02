import datetime
from unittest import mock

import pytest
from wagtail.api.conf import APIField

from tests.fakes.factories.cms.topics_list_page_factory import FakeTopicsListPageFactory


class TestTopicsListPage:
    @pytest.mark.parametrize(
        "expected_api_field_name",
        (
            "title",
            "page_description",
            "body",
            "last_published_at",
            "seo_title",
            "search_description",
        ),
    )
    def test_has_correct_api_fields(
        self,
        expected_api_field_name: str,
    ):
        """
        Given a blank `TopicsListPage` model
        When `api_feilds` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        blank_page = FakeTopicsListPageFactory.build_blank_page()

        # When
        api_fields: list[APIField] = blank_page.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field_name in api_field_names

    @pytest.mark.parametrize(
        "expected_content_panel", ["title", "page_description", "body"]
    )
    def test_has_correct_content_panels(
        self,
        expected_content_panel: str,
    ):
        """
        Given a blank `TopicsListPage` model
        when the expected panel name is called
        Then the panel value can be accessed from the page model
        """
        # Given
        blank_page = FakeTopicsListPageFactory.build_blank_page()

        # When / Then
        assert hasattr(blank_page, expected_content_panel)

    def test_is_previewable_returns_false(self):
        """
        Given a blank `TopcisListPage` model
        when the exptected panel name is called
        Then the panel value can be accessed from the page model
        """
        # Given
        blank_page = FakeTopicsListPageFactory.build_blank_page()

        # When
        page_is_previewable: bool = blank_page.is_previewable()

        # Then
        assert not page_is_previewable
