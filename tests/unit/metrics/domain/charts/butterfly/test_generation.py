from decimal import Decimal

import plotly.graph_objects as go
import pytest

from metrics.domain.charts.butterfly.generation import (
    InvalidButterflyChartSegmentsError,
    generate_butterfly,
)
from metrics.domain.models.plots import (
    ChartGenerationPayload,
    PlotGenerationData,
    PlotParameters,
)

HEIGHT = 400
WIDTH = 640

LEFT_HAND_SIDE_COLOUR = "COLOUR_1_DARK_BLUE"
RIGHT_HAND_SIDE_COLOUR = "COLOUR_4_ORANGE"

PRIMARY_FIELD_VALUES = ["00-04", "05-11", "12-17"]
DEFAULT_SEGMENTS = (
    ("m", LEFT_HAND_SIDE_COLOUR, "Male"),
    ("f", RIGHT_HAND_SIDE_COLOUR, "Female"),
)


def _build_plot_data(
    *,
    primary_field_value: str,
    sex: str,
    colour: str,
    label: str,
    metric_value: int,
) -> PlotGenerationData:
    plot_parameters = PlotParameters(
        chart_type="butterfly",
        topic="Lyme-disease",
        metric="lyme-disease_headline_cases",
        stratum="default",
        geography="England",
        geography_type="Nation",
        sex=sex,
        age=primary_field_value,
        x_axis="age",
        y_axis="metric",
        line_colour=colour,
        label=label,
    )
    return PlotGenerationData(
        parameters=plot_parameters,
        x_axis_values=[primary_field_value],
        y_axis_values=[Decimal(metric_value)],
    )


def _build_chart_generation_payload(
    *,
    segments: tuple[tuple[str, str, str], ...] = DEFAULT_SEGMENTS,
    **kwargs,
) -> ChartGenerationPayload:
    plots = [
        _build_plot_data(
            primary_field_value=primary_field_value,
            sex=sex,
            colour=colour,
            label=label,
            metric_value=(index + 1) * 100,
        )
        for index, primary_field_value in enumerate(PRIMARY_FIELD_VALUES)
        for sex, colour, label in segments
    ]

    return ChartGenerationPayload(
        chart_width=WIDTH,
        chart_height=HEIGHT,
        plots=plots,
        x_axis_title="Age group",
        y_axis_title="Cases",
        secondary_category="sex",
        **kwargs,
    )


class TestGenerateButterfly:
    def test_returns_one_trace_for_each_side_of_the_chart(self):
        """
        Given a dual category payload containing 2 segments
        When `generate_butterfly()` is called
        Then a figure with 1 horizontal bar trace per segment is returned
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        assert isinstance(figure, go.Figure)
        assert len(figure.data) == 2
        assert all(trace.orientation == "h" for trace in figure.data)

    def test_primary_field_values_are_plotted_on_the_y_axis(self):
        """
        Given a dual category payload containing primary field values
        When `generate_butterfly()` is called
        Then each trace is plotted against the primary field values on the y-axis
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        for trace in figure.data:
            assert list(trace.y) == PRIMARY_FIELD_VALUES

    def test_first_segment_is_mirrored_onto_the_left_hand_side(self):
        """
        Given a dual category payload containing 2 segments
        When `generate_butterfly()` is called
        Then the values for the first segment are negated
        And the values for the second segment are left as positive numbers
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        left_hand_side_trace, right_hand_side_trace = figure.data
        assert list(left_hand_side_trace.x) == [-100.0, -200.0, -300.0]
        assert list(right_hand_side_trace.x) == [100.0, 200.0, 300.0]

    def test_absolute_values_are_retained_for_hover_text(self):
        """
        Given a dual category payload containing 2 segments
        When `generate_butterfly()` is called
        Then the mirrored left hand side trace retains
            the absolute values as its `customdata`
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        left_hand_side_trace = figure.data[0]
        assert list(left_hand_side_trace.customdata) == [100.0, 200.0, 300.0]

    def test_segment_labels_are_used_for_the_plot_legend(self):
        """
        Given a dual category payload containing labelled segments
        When `generate_butterfly()` is called
        Then the segment labels are used as the trace names
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        assert [trace.name for trace in figure.data] == ["Male", "Female"]

    def test_falls_back_to_the_secondary_field_value_when_no_label_is_provided(self):
        """
        Given a dual category payload containing segments without labels
        When `generate_butterfly()` is called
        Then the secondary category values are used as the trace names
        """
        # Given
        chart_payload = _build_chart_generation_payload(
            segments=(
                ("m", LEFT_HAND_SIDE_COLOUR, ""),
                ("f", RIGHT_HAND_SIDE_COLOUR, ""),
            ),
        )

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        assert [trace.name for trace in figure.data] == ["m", "f"]

    def test_selected_colours_are_applied_to_each_side(self):
        """
        Given a dual category payload containing segments with selected colours
        When `generate_butterfly()` is called
        Then the corresponding RGBA colours are applied to each trace
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        assert [trace.marker.color for trace in figure.data] == [
            "rgba(18, 67, 109, 1)",
            "rgba(244, 106, 37, 1)",
        ]

    def test_applies_the_butterfly_chart_layout(self):
        """
        Given a dual category payload containing 2 segments
        When `generate_butterfly()` is called
        Then the butterfly layout is applied to the figure
        """
        # Given
        chart_payload = _build_chart_generation_payload(legend_title="Sex")

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        assert figure.layout.barmode == "overlay"
        assert figure.layout.yaxis.type == "category"
        assert figure.layout.yaxis.title.text == "Age group"
        assert figure.layout.xaxis.title.text == "Cases"
        assert figure.layout.legend.title.text == "<b>Sex</b>"

    @pytest.mark.parametrize(
        "segments",
        (
            (("m", LEFT_HAND_SIDE_COLOUR, "Male"),),
            (
                ("m", LEFT_HAND_SIDE_COLOUR, "Male"),
                ("f", RIGHT_HAND_SIDE_COLOUR, "Female"),
                ("all", "COLOUR_2_TURQUOISE", "All"),
            ),
        ),
    )
    def test_raises_error_when_segment_count_is_not_two(
        self, segments: tuple[tuple[str, str, str], ...]
    ):
        """
        Given a dual category payload which does not contain exactly 2 segments
        When `generate_butterfly()` is called
        Then an `InvalidButterflyChartSegmentsError` is raised
        """
        # Given
        chart_payload = _build_chart_generation_payload(segments=segments)

        # When / Then
        with pytest.raises(InvalidButterflyChartSegmentsError):
            generate_butterfly(chart_generation_payload=chart_payload)


class TestGenerateButterflyAggregatesCategories:
    def test_draws_one_bar_per_category_when_a_plot_holds_multiple_data_points(self):
        """
        Given a dual category payload whose plots each hold multiple
            data points for the same primary field value,
            as happens when the metric is sourced from timeseries data
        When `generate_butterfly()` is called
        Then a single bar is drawn per primary field value, per side,
            rather than one overlapping bar per underlying data point
        """
        # Given
        plots = [
            PlotGenerationData(
                parameters=_build_plot_data(
                    primary_field_value="00-04",
                    sex=sex,
                    colour=colour,
                    label=label,
                    metric_value=1,
                ).parameters,
                # 3 data points, eg. one per week of timeseries data
                x_axis_values=["00-04", "00-04", "00-04"],
                y_axis_values=[Decimal(1), Decimal(2), Decimal(3)],
            )
            for sex, colour, label in DEFAULT_SEGMENTS
        ]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=plots,
            x_axis_title="Age group",
            y_axis_title="Cases",
            secondary_category="sex",
        )

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        for trace in figure.data:
            assert list(trace.y) == ["00-04"]
            assert len(trace.x) == 1

    def test_uses_the_last_recorded_data_point_for_each_category(self):
        """
        Given a dual category payload whose plots hold
            multiple data points for the same primary field value
        When `generate_butterfly()` is called
        Then the last recorded data point is drawn for that category,
            matching how the dual category tables reduce the same plots
        """
        # Given
        plots = [
            PlotGenerationData(
                parameters=_build_plot_data(
                    primary_field_value="00-04",
                    sex=sex,
                    colour=colour,
                    label=label,
                    metric_value=1,
                ).parameters,
                x_axis_values=["00-04", "00-04", "00-04"],
                y_axis_values=[Decimal(1), Decimal(2), Decimal(7)],
            )
            for sex, colour, label in DEFAULT_SEGMENTS
        ]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=plots,
            x_axis_title="Age group",
            y_axis_title="Cases",
            secondary_category="sex",
        )

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        left_hand_side_trace, right_hand_side_trace = figure.data
        assert list(left_hand_side_trace.x) == [-7.0]
        assert list(right_hand_side_trace.x) == [7.0]


class TestGenerateButterflySideOrdering:
    def test_first_requested_segment_is_drawn_on_the_left_when_a_plot_is_dropped(self):
        """
        Given a dual category payload where the first requested segment
            returned no data for the first primary field value,
            and so was dropped before the chart was generated
        When `generate_butterfly()` is called
        Then the first requested segment is still drawn
            on the left hand side of the chart
        """
        # Given
        plots = [
            # The "m" segment is missing for the first age band
            _build_plot_data(
                primary_field_value="00-04",
                sex="f",
                colour=RIGHT_HAND_SIDE_COLOUR,
                label="Female",
                metric_value=100,
            ),
            _build_plot_data(
                primary_field_value="05-11",
                sex="m",
                colour=LEFT_HAND_SIDE_COLOUR,
                label="Male",
                metric_value=200,
            ),
            _build_plot_data(
                primary_field_value="05-11",
                sex="f",
                colour=RIGHT_HAND_SIDE_COLOUR,
                label="Female",
                metric_value=300,
            ),
        ]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=plots,
            x_axis_title="Age group",
            y_axis_title="Cases",
            secondary_category="sex",
            secondary_field_values=["m", "f"],
        )

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        left_hand_side_trace, right_hand_side_trace = figure.data
        assert left_hand_side_trace.name == "Male"
        assert right_hand_side_trace.name == "Female"

    def test_both_sides_are_aligned_against_the_same_categories(self):
        """
        Given a dual category payload where one segment
            returned no data for one of the primary field values
        When `generate_butterfly()` is called
        Then both traces are plotted against the same ordered categories,
            with a gap left where the missing value would have been
        """
        # Given
        plots = [
            _build_plot_data(
                primary_field_value="00-04",
                sex="f",
                colour=RIGHT_HAND_SIDE_COLOUR,
                label="Female",
                metric_value=100,
            ),
            _build_plot_data(
                primary_field_value="05-11",
                sex="m",
                colour=LEFT_HAND_SIDE_COLOUR,
                label="Male",
                metric_value=200,
            ),
            _build_plot_data(
                primary_field_value="05-11",
                sex="f",
                colour=RIGHT_HAND_SIDE_COLOUR,
                label="Female",
                metric_value=300,
            ),
        ]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=plots,
            x_axis_title="Age group",
            y_axis_title="Cases",
            secondary_category="sex",
            secondary_field_values=["m", "f"],
        )

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        left_hand_side_trace, right_hand_side_trace = figure.data
        assert list(left_hand_side_trace.y) == ["00-04", "05-11"]
        assert list(right_hand_side_trace.y) == ["00-04", "05-11"]
        # No "Male" value was available for the first age band
        assert list(left_hand_side_trace.x) == [None, -200.0]
        assert list(right_hand_side_trace.x) == [100.0, 300.0]


class TestGenerateButterflyValueAxis:
    def test_y_axis_categories_are_pinned_to_the_requested_order(self):
        """
        Given a dual category payload containing primary field values
        When `generate_butterfly()` is called
        Then the y-axis categories are pinned to the requested order,
            so that they cannot be re-ordered by the charting library
        """
        # Given
        chart_payload = _build_chart_generation_payload()

        # When
        figure = generate_butterfly(chart_generation_payload=chart_payload)

        # Then
        assert figure.layout.yaxis.categoryorder == "array"
        assert list(figure.layout.yaxis.categoryarray) == PRIMARY_FIELD_VALUES
