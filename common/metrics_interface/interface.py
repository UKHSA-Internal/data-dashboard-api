from metrics.data.models import core_models


class MetricsAPIInterface:
    @staticmethod
    def get_topic_manager():
        return core_models.Topic.objects

    @staticmethod
    def get_metric_manager():
        return core_models.Metric.objects

    @staticmethod
    def get_geography_type_manager():
        return core_models.GeographyType.objects

    @staticmethod
    def get_geography_manager():
        return core_models.Geography.objects
