import pytest

from metrics.data.models.core_models import Metric
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
