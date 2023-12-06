from unittest import mock

import pytest
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.search.index import SearchField

from cms.metrics_documentation.models.parent import (
    MetricsDocumentationMultipleLivePagesError,
    MetricsDocumentationParentPage,
    MetricsDocumentationSlugNotValidError,
)
from tests.fakes.factories.cms.metrics_documentation_factory import (
    FakeMetricsDocumentationParentPageFactory,
)
from tests.fakes.models.queryset import FakeQuerySet


class TestMetricsDocumentationParentPage:
    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "date_posted",
            "body",
            "related_links",
            "last_published_date",
            "seo_title",
            "search_description",
        ],
    )
    def test_has_correct_api_fields(
        self,
        expected_api_field: str,
    ):
        """
        Given a blank `MetricsDocumentationParentPage` model.
        When `api_fields` is called.
        Then the expected names are on the returned `APIField` objects.
        """
        # Given
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )

        # When
        api_fields: list[APIField] = fake_metrics_documentation_parent_page.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field in api_field_names

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "title",
            "date_posted",
            "body",
        ],
    )
    def test_has_the_correct_content_panels(
        self,
        expected_content_panel_name: str,
    ):
        """
        Given a blank `MetricsDocumentationParentPage` model.
        When `content_panels` is called.
        Then the expected names are on the returned `FieldPanel` objects.
        """
        # Given
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )

        # When
        content_panels: list[
            FieldPanel
        ] = fake_metrics_documentation_parent_page.content_panels

        # Then
        content_panel_names: set[str] = {
            content_panel.field_name for content_panel in content_panels
        }
        assert expected_content_panel_name in content_panel_names

    @pytest.mark.parametrize(
        "expected_search_field",
        [
            "body",
            "title",
            "id",
        ],
    )
    def test_has_correct_search_fields(
        self,
        expected_search_field: str,
    ):
        """
        Given a blank `MetricsDocumentationParentPage` model.
        When `search_field` is called.
        Then the expected names are on the returned `APIField` objects.
        """
        # Given
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )

        # When
        search_fields: list[SearchField] = fake_metrics_documentation_parent_page.search_fields

        # Then
        search_fields: set[str] = {api_field.field_name for api_field in search_fields}
        assert expected_search_field in search_fields

    @mock.patch.object(
        MetricsDocumentationParentPage, "_raise_error_if_slug_not_metrics_documentation"
    )
    @mock.patch.object(
        MetricsDocumentationParentPage, "_raise_error_for_multiple_live_pages"
    )
    def test_clean_delegates_extra_validation_calls(
        self,
        spy_raise_error_for_multiple_live_pages: mock.MagicMock,
        spy_raise_error_if_slug_not_metrics_documentation: mock.MagicMock,
    ):
        """
        Given a `MetricsDocumentationParentPage`
        When `clean()` is called from that model
        Then the extra validation methods are called out to.

        Patches:
            `spy_raise_error_for_multiple_live_pages`: To check validation
                is performed for preventing multiple live pages.
            `spy_raise_error_if_slug_not_metrics_documentation`: to check validation
                is performed for preventing a slug which does not
                contain `metrics_documentation`
        """
        # Given
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_parent_page.clean()

        # Then
        spy_raise_error_for_multiple_live_pages.assert_called_once()
        spy_raise_error_if_slug_not_metrics_documentation.assert_called_once()

    @mock.patch.object(
        MetricsDocumentationParentPage, "_raise_error_if_slug_not_metrics_documentation"
    )
    @mock.patch.object(
        MetricsDocumentationParentPage, "_raise_error_for_multiple_live_pages"
    )
    def test_clean_passes_for_trash_can_slug(
        self,
        spy_raise_error_for_multiple_live_pages: mock.MagicMock,
        spy_raise_error_if_slug_not_metrics_documentation: mock.MagicMock,
    ):
        """
        Given a `MetricsDocumentationParentPage` which has slug prefixed with `trash-`.
        When `clean()` is called from that model.
        Then the extra validation methods are called out to.

        Patches:
            `spy_raise_error_for_multiple_live_pages`: To check validation is
                performed for preventing multiple live pages.
            `spy_raise_error_if_slug_not_metrics_documentation`: To check validation
                is performed for preventing a slug which does not contain
                `metrics-documentation.

        """
        # Given
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )
        fake_metrics_documentation_parent_page.slug = "trash-metrics-documentation"

        # When
        fake_metrics_documentation_parent_page.clean()

        # Then
        spy_raise_error_for_multiple_live_pages.assert_called_once()
        spy_raise_error_if_slug_not_metrics_documentation.assert_called_once()

    def test_raise_error_if_slug_not_metrics_documentation(self):
        """
        Given an invalid slug which is not equal to `metrics-documentation`.
        When `_raise_error_if_slug_not_metrics_documentation()` is called.
        Then a `MetricsDocumentationParentSlugNotValidError` is raised
            and it provides the expected validation message.
        """
        # Given
        invalid_slug = "not-valid-slug"
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(
                slug=invalid_slug
            )
        )

        # When / Then
        with pytest.raises(MetricsDocumentationSlugNotValidError):
            fake_metrics_documentation_parent_page._raise_error_if_slug_not_metrics_documentation()

    def test_raise_error_if_slug_not_metrics_documentation_passes_for_valid_slug(self):
        """
        Given a slug which is equal to `MetricsDocumentation`.
        When `_raise_error_if_slug_not_metrics_documentation()` is called from
            an instance of a `MetricsDocumentationParentPage`.
        Then no error is raised.
        """
        # Given
        valid_slug = "metrics-documentation"
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(
                slug=valid_slug
            )
        )

        # When / Then
        fake_metrics_documentation_parent_page._raise_error_if_slug_not_metrics_documentation()

    @mock.patch.object(MetricsDocumentationParentPage, "objects")
    def test_raise_error_for_multiple_live_pages_passes_for_no_current_live_pages(
        self,
        spy_metrics_documentation_parent_page_model_manager: mock.MagicMock,
    ):
        """
        Given a `MetricsDocumentationParentPage` model manager which returns no live pages.
        When `_raise_error_for_multiple_live_pages()` is called from an instance
            of `MetricsDocumentationParentPage`.
        Then no error is raised.
        """
        # Given
        fake_queryset = FakeQuerySet(instances=[])
        spy_metrics_documentation_parent_page_model_manager.get_live_pages.return_value = (
            fake_queryset
        )
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )

        # When / Then
        fake_metrics_documentation_parent_page._raise_error_for_multiple_live_pages()

    @mock.patch.object(MetricsDocumentationParentPage, "objects")
    def test_raise_error_for_multiple_live_pages_passes_for_current_page_being_republished(
        self,
        spy_metrics_documentation_parent_page_model_manager: mock.MagicMock,
    ):
        """
        Given a `MetricsDocumentationParentPage` model which returns only the current live page.
        When `_raise_error_for_multiple_live_pages()` is called from an instance
            of `MetricsDocumentationParentPage`
        Then no error is raised.

        Patches:
            `spy_metrics_documentation_page_model_manager`: To isolate the model manager and
                emulate the returned queryset from the database.
        """
        # Given
        fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template()
        )
        fake_queryset = FakeQuerySet(instances=[fake_metrics_documentation_parent_page])
        spy_metrics_documentation_parent_page_model_manager.get_live_pages.return_value = (
            fake_queryset
        )

        # When / Then
        fake_metrics_documentation_parent_page._raise_error_for_multiple_live_pages()

    @mock.patch.object(MetricsDocumentationParentPage, "objects")
    def test_raise_error_for_multiple_live_pages_raises_error(
        self,
        spy_metrics_documentation_parent_page_model_manager: mock.MagicMock,
    ):
        """
        Given a `MetricsDocumentationParentPage` model manager which returns
            a different live page from the current page.
        When `_raise_error_for_multiple_live_pages()` is called from an
            instance of `MetricsDocumentationParentPage`.
        Then a `MetricsDocumentationParentMultipleLivePagesError` is raised
            and the correct error message provided.

        Patches:
            `spy_metrics_documentation_parent_page_model_manager: To isolate the
                model manager and emulate the returned queryset from the database.

        """
        # Given
        current_fake_metrics_documentation_parent_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(pk=1)
        )
        fake_queryset = FakeQuerySet(
            instances=[current_fake_metrics_documentation_parent_page]
        )
        spy_metrics_documentation_parent_page_model_manager.get_live_pages.return_value = (
            fake_queryset
        )

        invalid_duplicate_page = (
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(pk=2)
        )

        # When / Then
        with pytest.raises(MetricsDocumentationMultipleLivePagesError):
            invalid_duplicate_page._raise_error_for_multiple_live_pages()
