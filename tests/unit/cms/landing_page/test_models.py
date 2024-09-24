from unittest import mock

import pytest
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.api.conf import APIField

from cms.dashboard.models import UKHSAPage
from metrics.domain.common.utils import ChartTypes
from tests.fakes.factories.cms.landing_page_factory import FakeLandingPageFactory


class TestBlankLandingPage:
    @pytest.mark.parametrize(
        "expected_api_field_name",
        (
            "title",
            "sub_title",
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
        Given a blank `LandingPage` model
        When `api_fields` is called
        Then the expected names are on teh returned `APIField` objects
        """
        # Given
        blank_page = FakeLandingPageFactory.build_blank_page()

        # When
        api_fields: list[APIField] = blank_page.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field_name in api_field_names

    @pytest.mark.parametrize("expected_content_panel", ["title", "sub_title", "body"])
    def test_has_correct_content_panels(
        self,
        expected_content_panel: str,
    ):
        """
        Given a blank `LandingPage` model
        When `content_panels` is called
        Then the expected names are on the returned `FieldPanel` objects
        """
        # Given
        blank_page = FakeLandingPageFactory.build_blank_page()

        # When
        content_panels: list[FieldPanel] = blank_page.content_panels

        # Then
        content_panels_names: set[str] = {p.field_name for p in content_panels}
        assert expected_content_panel in content_panels_names

    def test_is_previewable_returns_false(self):
        """
        Given a blank `LandingPage` model
        When `is_previewable()` is called
        Then False is returned
        """
        # Given
        blank_page = FakeLandingPageFactory.build_blank_page()

        # When
        page_is_previewable: bool = blank_page.is_previewable()

        # Then
        assert not page_is_previewable

    @mock.patch.object(UKHSAPage, "get_url_parts")
    def test_get_url_paths(self, mocked_super_get_url_parts: mock.MagicMock):
        """
        Given a `LandingPage` model
        When `get_url_parts()` is called
        Then the url parts are returned with
            an empty string representing the page path
        """
        # Given
        expected_site_id = 123
        root_url = "https://my-prefix.dev.ukhsa-data-dashboard.gov.uk"
        page_path = "topics"
        mocked_super_get_url_parts.return_value = (
            expected_site_id,
            root_url,
            page_path,
        )
        blank_page = FakeLandingPageFactory.build_blank_page()

        # When
        url_parts: tuple[int, str, str] = blank_page.get_url_parts(request=mock.Mock())

        # Then
        assert url_parts[0] == expected_site_id
        assert url_parts[1] == root_url
        assert url_parts[2] == "" != page_path
