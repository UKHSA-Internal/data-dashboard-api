from unittest.mock import MagicMock, patch

import pytest
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.api.conf import APIField

from cms.auth_content.forms.non_public_page import THEME_FIELD
from cms.metrics_documentation.models import MetricsDocumentationChildEntry
from tests.fakes.factories.cms.metrics_documentation_child_entry_factory import (
    FakeMetricsDocumentationChildEntryFactory,
)
from tests.fakes.models.cms.metrics_documentation_child import (
    FakeMetricsDocumentationChildEntry,
)


class TestMetricsDocumentationChildEntryAdminForm:

    @patch("cms.metrics_documentation.models.child.get_all_unique_metric_names")
    # swap the parent NonPublicAdminForm init for its parent WagtailAdminPageForm init to avoid mocking a load of stuff
    # we need to actually do this test on the MetricsDocumentationChildEntryAdminForm
    @patch(
        "cms.auth_content.forms.non_public_page.NonPublicPageAdminForm.__init__",
        WagtailAdminPageForm.__init__,
    )
    def test_metric_choices_are_loaded(
        self, mock_get_all_unique_metric_names: MagicMock
    ):
        """
        Given a set of mock metric names, a mock get_all_unique_metric_names function returning them, and a page
        When the form associated with a MetricsDocumentationChildEntry is instantiated
        Then the choices on the metric field widget should be filled in using the get_all_unique_metric_names response
        """
        expected = [
            ("1", "test"),
            ("2", "test2"),
            ("3", "test3"),
        ]
        mock_get_all_unique_metric_names.configure_mock(return_value=expected)
        page = FakeMetricsDocumentationChildEntry()

        form = page.get_edit_handler().get_form_class()(instance=page)

        assert form.fields["metric"].widget.choices == [
            ("", "----------"),
            *expected,
        ]


class TestMetricsDocumentationChildEntry:
    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "title",
            "metric",
            "body",
            "is_public",
            "page_classification",
            "last_updated_at",
            "last_published_at",
            "page_description",
            "topic",
            "metric_group",
        ],
    )
    def test_has_correct_api_fields(self, expected_api_field: str):
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
            "is_public",
            "non_public_page_options",
            "page_description",
            "metric",
            "body",
        ],
    )
    def test_has_the_correct_content_panels(
        self,
        expected_content_panel_name: str,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model
        Then the expected content panels are specified
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # Then
        assert expected_content_panel_name in [
            panel.clean_name
            for panel in fake_metrics_documentation_child_entry_page.content_panels
            if hasattr(panel, "clean_name")
        ]

    @pytest.mark.parametrize(
        "metric, metric_group",
        [
            ("COVID-19_cases_rateRollingMean", "cases"),
            ("COVID-19_headline_vaccines_autumn23Total", "headline"),
            ("COVID-19_vaccinations_autumn22_uptakeByDay", "vaccinations"),
            ("COVID-19_deaths_ONSByWeek", "deaths"),
        ],
    )
    def test_metric_group_returns_expected_string(self, metric: str, metric_group: str):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model with a metric set
        Then the metric_group will be correctly extracted from the string.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template(
                metric=metric
            )
        )

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == metric_group

    @pytest.mark.parametrize(
        "metric",
        ["COVID-19casesrateRollingMean", "COVID-19_", "", None],
    )
    def test_metric_group_returns_emptry_string_with_missing_values(self, metric: str):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model with a metric set
        Then the metric_group will return an empty string.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template(
                metric=metric
            )
        )

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == ""
