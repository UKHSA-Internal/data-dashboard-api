from rest_framework import serializers
from metrics.api.serializers.charts import ChartPlotsListSerializer
from metrics.api.serializers import help_texts


class TabularSerializer(serializers.Serializer):
    plots = ChartPlotsListSerializer()


class TabularResponseSerializer(serializers.Serializer):
    date = serializers.CharField(help_text=help_texts.TABULAR_RESPONSE_HELP_TEXT)
    plot_value = serializers.CharField(help_text=help_texts.TABULAR_RESPONSE_HELP_TEXT)
