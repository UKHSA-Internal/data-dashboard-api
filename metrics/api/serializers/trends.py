from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.api.serializers.headlines import HeadlinesQuerySerializer
from metrics.domain.models.trends import TrendsParameters


class TrendsQuerySerializer(HeadlinesQuerySerializer):
    percentage_metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.TREND_PERCENTAGE_METRIC_NAME_FIELD,
    )

    def populate_choices(self):
        super().populate_choices()
        self.fields["percentage_metric"].choices = (
            self.metric_manager.get_all_unique_percent_change_type_names()
        )

    def to_models(self, request: Request) -> TrendsParameters:
        return TrendsParameters(**self.validated_data, request=request)


class TrendsResponseSerializer(serializers.Serializer):
    metric_name = serializers.CharField(help_text=help_texts.TREND_METRIC_NAME_FIELD)
    metric_value = serializers.FloatField(help_text=help_texts.TREND_METRIC_VALUE_FIELD)

    percentage_metric_name = serializers.CharField(
        help_text=help_texts.TREND_PERCENTAGE_METRIC_NAME_FIELD
    )
    percentage_metric_value = serializers.FloatField(
        help_text=help_texts.TREND_METRIC_VALUE_FIELD
    )

    direction = serializers.CharField(help_text=help_texts.DIRECTION_FIELD)
    colour = serializers.CharField(help_text=help_texts.COLOUR_FIELD)
