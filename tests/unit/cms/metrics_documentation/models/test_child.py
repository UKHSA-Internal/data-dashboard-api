from unittest import mock

from django.core.exceptions import ValidationError
import pytest
from wagtail.admin.panels import FieldPanel
from wagtail.api.conf import APIField

from tests.fakes.factories.cms.metrics_documentation_child_entry_factory import (
    FakeMetricsDocumentationChildEntryFactory,
)

MODULE_PATH = "cms.metrics_documentation.models.child"


class TestMetricsDocumentationChildEntry:
    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "title",
            "body",
            "metric",
            "metric_group",
            "topic",
            "last_updated_at",
            "last_published_at",
            "page_description",
            "is_public",
            "page_classification",
        ],
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_has_correct_api_fields(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        expected_api_field: str,
    ):
        """
        Given blank `MetricsDocumentationChildEntryPage` model.
        When `api_fields` is called.
        Then the expected names are on the returned `APIField` objects.
        """
        # Given
        fake_metrics_documentation_child_entry = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        api_fields: list[APIField] = fake_metrics_documentation_child_entry.api_fields

        # Then
        api_fields_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field in api_fields_names

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "page_description",
            "metric",
            "body",
        ],
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_has_the_correct_content_panels(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        expected_content_panel_name: str,
    ):
        """
        Give a blank `MetricsDocumentationChildEntryPage` model.
        When the expected content panel name is called
        Then the panel value can be accessed from the page model
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        content_panels: list[FieldPanel] = (
            fake_metrics_documentation_child_entry_page.content_panels
        )

        # Then
        assert hasattr(
            fake_metrics_documentation_child_entry_page, expected_content_panel_name
        )

    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    @pytest.mark.parametrize(
        "metric_id, metric_group",
        [
            (1, "cases"),
            (2, "headline"),
            (3, "vaccinations"),
            (4, "deaths"),
        ],
    )
    def test_metric_group_returns_expected_string(
        self,
        get_all_metric_names_and_ids: mock.MagicMock,
        metric_id: int,
        metric_group: str,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric id is supplied to the `metric` property.
        Then the metric_group will be correctly extracted from the string.
        """
        # Given
        get_all_metric_names_and_ids.return_value = [
            (1, "COVID-19_cases_rateRollingMean"),
            (2, "COVID-19_headline_vaccines_autumn23Total"),
            (3, "COVID-19_vaccinations_autumn22_uptakeByDay"),
            (4, "COVID-19_deaths_ONSByWeek"),
        ]
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = metric_id

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == metric_group

    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    @pytest.mark.parametrize(
        "metric_id",
        [1,2,3,4,5],
    )
    def test_metric_group_returns_emptry_string_with_missing_values(self, get_all_metric_names_and_ids: mock.MagicMock, metric_id: int):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric id is supplied to the `metric` property with invalid choices returned.
        Then the metric_group will return an empty string.
        """
        # Given
        get_all_metric_names_and_ids.return_value = [
            (1, "COVID-19casesrateRollingMean"),
            (2, "COVID-19_"),
            (3, ""),
            (4, None),
        ]
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = metric_id
        
        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == ""

    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_metric_group_returns_emptry_string_with_empty_metrics(self, get_all_metric_names_and_ids: mock.MagicMock):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric id is supplied to the `metric` property with no choices returned.
        Then the metric_group will return an empty string.
        """
        # Given
        get_all_metric_names_and_ids.return_value = []
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = 1
        
        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == ""

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_error_raised_if_invalid_classification(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When no page classification is given.
        Then a `ValidationError` is raised.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = None

        # When/Then
        with pytest.raises(ValidationError):
            fake_metrics_documentation_child_entry_page.clean()

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_page_clears_page_classification(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is True (i.e the page is a public page).
        When a page classification is given.
        Then the page classification level is cleared.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = True
        fake_metrics_documentation_child_entry_page.page_classification = "official"

        # When
        fake_metrics_documentation_child_entry_page.clean()

        # Then
        assert fake_metrics_documentation_child_entry_page.page_classification is None

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_non_public_page_doesnt_clean_page_classification(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When a page classification is given.
        Then the page classification level is kept.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = "official"
        fake_metrics_documentation_child_entry_page.theme = "infectious_disease"
        fake_metrics_documentation_child_entry_page.sub_theme = "respiratory"
        fake_metrics_documentation_child_entry_page.topic = "COVID-19"

        # When
        fake_metrics_documentation_child_entry_page.clean()

        # Then
        assert (
            fake_metrics_documentation_child_entry_page.page_classification
            == "official"
        )
