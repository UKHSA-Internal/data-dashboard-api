import contextlib

from django.db.utils import OperationalError
from rest_framework import serializers

from metrics.api.serializers import help_texts, plots
from metrics.domain.models import PlotsCollection
from metrics.domain.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    ChartTypes,
)


class TablePlotSerializer(plots.PlotSerializer):
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.choices(),
        required=False,
        default="simple_line",
    )

    label = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.LABEL_FIELD,
    )


class TablePlotsListSerializer(serializers.ListSerializer):
    child = TablePlotSerializer()


class TablesSerializer(serializers.Serializer):
    plots = TablePlotsListSerializer()
    x_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_X_AXIS,
        default=DEFAULT_X_AXIS,
    )
    y_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_Y_AXIS,
        default=DEFAULT_Y_AXIS,
    )

    def __init__(self, *args, **kwargs):
        with contextlib.suppress(OperationalError):
            super().__init__(*args, **kwargs)

    def to_models(self) -> PlotsCollection:
        return PlotsCollection(
            plots=self.data["plots"],
            file_format="svg",
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            x_axis=self.data.get("x_axis") or DEFAULT_X_AXIS,
            y_axis=self.data.get("y_axis") or DEFAULT_Y_AXIS,
        )


class TablesResponseValueSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.CharField()


class TablesResponseValuesListSerializer(serializers.ListSerializer):
    child = TablesResponseValueSerializer()


class TablesResponsePlotsListSerializer(serializers.Serializer):
    reference = serializers.CharField()
    values = TablesResponseValuesListSerializer()


class TablesResponseSerializer(serializers.ListSerializer):
    child = TablesResponsePlotsListSerializer()
