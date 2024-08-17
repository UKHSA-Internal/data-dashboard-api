import pytest

from metrics.data.models.core_models import Metric, MetricGroup
from tests.factories.metrics.metric import MetricFactory


class TestMetricManager:

    @pytest.mark.django_db
    def test_get_all_unique_change_type_names(self):
        """
        Given a number of existing `Metric` records
        When `get_all_unique_change_type_names()` is called
            from the `MetricManager`
        Then the metrics returned have been filtered correctly
        """
        # Given
        change_type_metric_name = "COVID-19_headline_ONSdeaths_7DayChange"
        MetricFactory.create(name=change_type_metric_name)
        MetricFactory.create(name="COVID-19_deaths_ONSByWeek")

        # When
        all_unique_change_type_metrics = (
            Metric.objects.get_all_unique_change_type_names()
        )

        # Then
        assert all_unique_change_type_metrics.count() == 1
        assert change_type_metric_name in all_unique_change_type_metrics.values_list(
            "name", flat=True
        )

    @pytest.mark.django_db
    def test_get_all_timeseries_metric_names(self):
        """
        Given a number of existing `Metric` records
        When `get_all_timeseries_metric_names()` is called
            from the `MetricManager`
        Then the metrics returned have been filtered correctly
        """
        # Given
        timeseries_metric_name = "COVID-19_deaths_ONSByWeek"
        timeseries_metric_group = MetricGroup.objects.create(name="deaths")
        Metric.objects.create(
            name=timeseries_metric_name,
            metric_group=timeseries_metric_group,
        )
        headline_metric_group = MetricGroup.objects.create(name="headline")
        Metric.objects.create(
            name="COVID-19_headline_ONSdeaths_7DayChange",
            metric_group=headline_metric_group,
        )

        # When
        all_timeseries_metric_names = Metric.objects.get_all_timeseries_names()

        # Then
        assert all_timeseries_metric_names.count() == 1
        assert timeseries_metric_name in all_timeseries_metric_names.values_list(
            "name", flat=True
        )
