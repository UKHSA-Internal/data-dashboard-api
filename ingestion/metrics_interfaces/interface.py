from typing import Callable

from metrics.data.enums import TimePeriod
from metrics.data.models import core_models
from metrics.data.operations.ingestion import (
    create_core_and_api_timeseries,
    create_core_headlines,
)


class MetricsAPIInterface:
    @staticmethod
    def get_theme_manager():
        return core_models.Theme.objects

    @staticmethod
    def get_sub_theme_manager():
        return core_models.SubTheme.objects

    @staticmethod
    def get_topic_manager():
        return core_models.Topic.objects

    @staticmethod
    def get_metric_group_manager():
        return core_models.MetricGroup.objects

    @staticmethod
    def get_metric_manager():
        return core_models.Metric.objects

    @staticmethod
    def get_geography_type_manager():
        return core_models.GeographyType.objects

    @staticmethod
    def get_geography_manager():
        return core_models.Geography.objects

    @staticmethod
    def get_age_manager():
        return core_models.Age.objects

    @staticmethod
    def get_stratum_manager():
        return core_models.Stratum.objects

    @staticmethod
    def get_core_headline_manager():
        return core_models.CoreHeadline.objects

    @staticmethod
    def get_core_timeseries_manager():
        return core_models.CoreTimeSeries.objects

    @staticmethod
    def get_time_period_enum() -> TimePeriod:
        return TimePeriod

    @staticmethod
    def get_create_core_headlines() -> Callable:
        return create_core_headlines

    @staticmethod
    def get_create_core_timeseries() -> Callable:
        return create_core_and_api_timeseries
