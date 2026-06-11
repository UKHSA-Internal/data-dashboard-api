import contextlib

from django.db.utils import OperationalError
from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.api.serializers.plots import PlotSerializer
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
)
from metrics.domain.models import ChartRequestParams


class DualCategoryTableSegmentSerializer(serializers.Serializer):
    colour = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.LABEL_FIELD,
    )

    secondary_field_value = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.LABEL_FIELD,
    )

    label = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.LABEL_FIELD,
    )


class DualCategoryTableSegmentListSerializer(serializers.ListSerializer):
    child = DualCategoryTableSegmentSerializer()


class DualCategoryTablesSerializer(serializers.Serializer):

    segments = DualCategoryTableSegmentListSerializer()

    static_fields = PlotSerializer()

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

    primary_field_values = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of primary field values for this segment",
        required=True,
        allow_empty=False,
    )

    secondary_category = serializers.CharField(
        help_text="Secondary category field for the chart",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        with contextlib.suppress(OperationalError):
            super().__init__(*args, **kwargs)

    def to_models(self, request: Request) -> ChartRequestParams:

        groups_plots = []
        primary_field_values = self.data.get("primary_field_values")
        x_axis = self.data.get("x_axis") or DEFAULT_X_AXIS
        y_axis = self.data.get("y_axis") or DEFAULT_Y_AXIS
        static_fields = self.data.get("static_fields")
        print(f"AIDAN static_fields {static_fields}")
        topic = static_fields.get("topic")

        for primary_field_value in primary_field_values:
            for segment in self.data["segments"]:
                plot = {
                    "y_axis": y_axis,
                    "x_axis": primary_field_value,
                    self.data.get("secondary_category"): segment[
                        "secondary_field_value"
                    ],
                    **static_fields,
                }
                groups_plots.append(plot)
        print(f"AIDAN: plots {groups_plots}")
        return ChartRequestParams(
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            file_format="svg",
            plots=groups_plots,
            request=request,
            x_axis=x_axis,
            y_axis=y_axis,
        )


class DualCategoryTablesResponseValueSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.CharField()
    in_reporting_delay_period = serializers.BooleanField()
    # Confidence intervals aren't implemented for dual category charts


class DualCategoryTablesResponseValuesListSerializer(serializers.ListSerializer):
    child = DualCategoryTablesResponseValueSerializer()


class DualCategoryTablesResponsePlotsListSerializer(serializers.Serializer):
    reference = serializers.CharField()
    values = DualCategoryTablesResponseValuesListSerializer()


class DualCategoryTablesResponseSerializer(serializers.ListSerializer):
    child = DualCategoryTablesResponsePlotsListSerializer()
