import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.downloads.dual_category import (
    DualCategoryDownloadSerializer,
)
from metrics.api.serializers.plots import PlotSerializer
from metrics.api.views.downloads.dual_category_downloads import (
    EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD,
)
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager

HEADLINE_METRIC = "COVID-19_headline_vaccines_spring24Uptake"
TIMESERIES_METRIC = "COVID-19_cases_rateRollingMean"


class TestDualCategoryDownloadSerializer:
    def test_to_models_expands_headline_plots(self):
        """
        Given a valid dual-category headline download payload
        When `to_models()` is called on `DualCategoryDownloadSerializer`
        Then one plot is created per primary field value and segment combination
        """
        # Given
        fake_metric = FakeMetricFactory.build_example_metric(
            metric_name=HEADLINE_METRIC,
            metric_group_name="headline",
        )
        fake_topic = fake_metric.metric_group.topic
        metric_manager = FakeMetricManager([fake_metric])
        topic_manager = FakeTopicManager([fake_topic])

        payload = EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD.copy()
        payload["static_fields"] = payload["static_fields"].copy()
        payload["static_fields"]["topic"] = fake_topic.name
        payload["static_fields"]["metric"] = HEADLINE_METRIC

        serializer_context = {
            "topic_manager": topic_manager,
            "metric_manager": metric_manager,
        }
        serializer = DualCategoryDownloadSerializer(
            data=payload,
            context=serializer_context,
        )
        serializer.fields["static_fields"] = PlotSerializer(context=serializer_context)
        serializer.is_valid(raise_exception=True)

        # When
        result: DualCategoryDownloadRequestParams = serializer.to_models(request=None)

        # Then
        assert len(result.plots) == 12
        assert result.secondary_category == "sex"
        assert result.segment_secondary_values == ["f", "m"]
        assert result.plots[0].age == "00-01"
        assert result.plots[0].sex == "f"
        assert result.plots[1].sex == "m"

    def test_to_models_expands_timeseries_plots(
        self, plot_serializer_payload_and_model_managers
    ):
        """
        Given a valid dual-category timeseries download payload
        When `to_models()` is called on `DualCategoryDownloadSerializer`
        Then one plot is created per segment with the secondary category applied
        """
        # Given
        plot_payload, metric_manager, topic_manager = (
            plot_serializer_payload_and_model_managers
        )
        payload = {
            "file_format": "json",
            "x_axis": "date",
            "y_axis": "metric",
            "chart_type": "stacked_bar",
            "static_fields": {
                "topic": plot_payload["topic"],
                "metric": plot_payload["metric"],
                "stratum": plot_payload.get("stratum", "default"),
                "age": "all",
                "geography": plot_payload.get("geography", "England"),
                "geography_type": plot_payload.get("geography_type", "Nation"),
                "sex": "all",
                "date_from": "2020-02-01",
                "date_to": "2021-02-01",
            },
            "secondary_category": "age",
            "segments": [
                {"secondary_field_value": "00-04"},
                {"secondary_field_value": "05-11"},
            ],
        }

        serializer_context = {
            "topic_manager": topic_manager,
            "metric_manager": metric_manager,
        }
        serializer = DualCategoryDownloadSerializer(
            data=payload,
            context=serializer_context,
        )
        serializer.fields["static_fields"] = PlotSerializer(context=serializer_context)
        serializer.is_valid(raise_exception=True)

        # When
        result = serializer.to_models(request=None)

        # Then
        assert len(result.plots) == 2
        assert result.plots[0].age == "00-04"
        assert result.plots[1].age == "05-11"
        assert result.primary_field_values == []

    def test_validation_requires_primary_field_values_for_headline(self):
        """
        Given a headline download payload without `primary_field_values`
        When `validate()` is called on `DualCategoryDownloadSerializer`
        Then a `ValidationError` is raised for `primary_field_values`
        """
        # Given
        payload = EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD.copy()
        payload.pop("primary_field_values")

        serializer = DualCategoryDownloadSerializer()

        # When / Then
        with pytest.raises(ValidationError) as error:
            serializer.validate(attrs=payload)

        assert "primary_field_values" in error.value.detail

    def test_validation_rejects_non_date_x_axis_for_timeseries(self):
        """
        Given a timeseries download payload with a non-date `x_axis`
        When `validate()` is called on `DualCategoryDownloadSerializer`
        Then a `ValidationError` is raised for `x_axis`
        """
        # Given
        payload = {
            "file_format": "json",
            "x_axis": "age",
            "static_fields": {"metric": TIMESERIES_METRIC},
            "secondary_category": "sex",
            "segments": [{"secondary_field_value": "f"}],
        }

        serializer = DualCategoryDownloadSerializer()

        # When / Then
        with pytest.raises(ValidationError) as error:
            serializer.validate(attrs=payload)

        assert "x_axis" in error.value.detail

    def test_validation_rejects_primary_field_values_for_timeseries(self):
        """
        Given a timeseries download payload with `primary_field_values`
        When `validate()` is called on `DualCategoryDownloadSerializer`
        Then a `ValidationError` is raised for `primary_field_values`
        """
        # Given
        payload = {
            "file_format": "json",
            "x_axis": "date",
            "static_fields": {"metric": TIMESERIES_METRIC},
            "secondary_category": "age",
            "segments": [{"secondary_field_value": "00-04"}],
            "primary_field_values": ["00-04"],
        }

        serializer = DualCategoryDownloadSerializer()

        # When / Then
        with pytest.raises(ValidationError) as error:
            serializer.validate(attrs=payload)

        assert "primary_field_values" in error.value.detail
