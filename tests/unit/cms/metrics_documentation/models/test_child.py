from unittest import mock

import pytest
from wagtail.admin.panels import FieldPanel
from wagtail.api.conf import APIField

from cms.metrics_documentation.models import child
from cms.metrics_documentation.models.child import (
    InvalidTopicForChosenMetricForChildEntryError,
)
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
            "is_public"
        ],
    )
    @mock.patch(f"{MODULE_PATH}.get_all_unique_metric_names")
    def test_has_correct_api_fields(
        self,
        mock_get_all_unique_metric_names: mock.MagicMock(),
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
    @mock.patch(f"{MODULE_PATH}.get_all_unique_metric_names")
    def test_has_the_correct_content_panels(
        self,
        mock_get_all_unique_metric_names: mock.MagicMock(),
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

    @mock.patch(f"{MODULE_PATH}.get_a_list_of_all_topic_names")
    @mock.patch.object(child.MetricsDocumentationChildEntry, "find_topic")
    @mock.patch(f"{MODULE_PATH}.get_all_unique_metric_names")
    def test_get_topic_delegates_calls_correctly(
        self,
        mock_get_all_unique_metric_names: mock.MagicMock,
        spy_find_topic: mock.MagicMock,
        spy_get_a_list_of_all_topic_names: mock.MagicMock,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When `get_topic()` is called.
        Then the `get_a_list_of_all_topic_names()` method and `find_topic()`
            methods are called.
        """
        # Given
        fake_topics = ["COVID-19", "Influenza"]
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )
        fake_metrics_documentation_child_entry_page.metric = (
            "COVID-19_cases_rateRollingMean"
        )

        # When
        spy_get_a_list_of_all_topic_names.return_value = fake_topics
        fake_metrics_documentation_child_entry_page.get_topic()

        # Then
        spy_get_a_list_of_all_topic_names.assert_called_once()
        spy_find_topic.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.get_a_list_of_all_topic_names")
    @mock.patch(f"{MODULE_PATH}.get_all_unique_metric_names")
    @pytest.mark.parametrize(
        "metric_name, metric_group",
        [
            ("COVID-19_cases_rateRollingMean", "cases"),
            ("COVID-19_headline_vaccines_autumn23Total", "headline"),
            ("COVID-19_vaccinations_autumn22_uptakeByDay", "vaccinations"),
            ("COVID-19_deaths_ONSByWeek", "deaths"),
        ],
    )
    def test_metric_group_returns_expected_string(
        self,
        mock_get_all_unique_metric_names: mock.MagicMock,
        mock_get_all_topic_names: mock.MagicMock,
        metric_name: str,
        metric_group: str,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric name is supplied to the `metric` property.
        Then the metric_group will be correctly extracted from the string.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = metric_name

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == metric_group

    @mock.patch(f"{MODULE_PATH}.get_all_unique_metric_names")
    @mock.patch(f"{MODULE_PATH}.get_a_list_of_all_topic_names")
    @pytest.mark.parametrize(
        "selected_metric, extracted_topic",
        [
            ("COVID-19_cases_rateRollingMean", "COVID-19"),
            ("influenza_headline_ICUHDUadmissionRatePercentChange", "Influenza"),
            ("hMPV_testing_positivityByWeek", "hMPV"),
            ("parainfluenza_headline_positivityLatest", "Parainfluenza"),
            ("rhinovirus_headline_positivityLatest", "Rhinovirus"),
            ("RSV_headline_admissionRateLatest", "RSV"),
            ("adenovirus_headline_positivityLatest", "Adenovirus"),
        ],
    )
    def test_find_topic_returns_expected_topic_name(
        self,
        spy_get_a_list_of_all_topic_names: mock.MagicMock(),
        mock_get_all_unique_metric_names: mock.MagicMock(),
        selected_metric: str,
        extracted_topic: str,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model
            a list of topics and a metric name.
        When the `find_topic()` method is called.
        Then the expected topic name will be matched from the list
            using the metric name.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )
        fake_topics = [
            "COVID-19",
            "Influenza",
            "RSV",
            "hMPV",
            "Parainfluenza",
            "Rhinovirus",
            "Adenovirus",
        ]
        fake_metrics_documentation_child_entry_page.metric = selected_metric

        # When
        return_topic = fake_metrics_documentation_child_entry_page.find_topic(
            topics=fake_topics
        )

        # Then
        assert return_topic == extracted_topic

    @mock.patch(f"{MODULE_PATH}.get_all_unique_metric_names")
    @mock.patch(f"{MODULE_PATH}.get_a_list_of_all_topic_names")
    def test_find_topic_raises_error(
        self,
        mock_get_a_list_of_all_topic_names: mock.MagicMock(),
        mock_get_all_unique_metric_names: mock.MagicMock(),
    ):
        """
        Given a metric name that does not include a valid topic.
        When the `find_topic()` method is called with a list of topics.
        Then an `InvalidTopicForChosenMetricForChildEntryError` is raised.
        """
        # Given
        fake_invalid_metric = "invalid_metric_contains_no_topic"
        fake_topics = [
            "COVID-19",
            "Influenza",
            "RSV",
            "hMPV",
            "Parainfluenza",
            "Rhinovirus",
            "Adenovirus",
        ]
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )
        fake_metrics_documentation_child_entry_page.metric = fake_invalid_metric

        # When / Then
        with pytest.raises(InvalidTopicForChosenMetricForChildEntryError):
            fake_metrics_documentation_child_entry_page.find_topic(topics=fake_topics)
