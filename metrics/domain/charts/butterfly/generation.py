import plotly.graph_objects as go

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.dual_category import DualCategoryChartSettings
from metrics.domain.models.plots import ChartGenerationPayload

BUTTERFLY_SIDES_COUNT = 2
LEFT_HAND_SIDE_INDEX = 0

BUTTERFLY_SEGMENT_COUNT_ERROR_MESSAGE = (
    "Butterfly charts require exactly 2 segments, "
    "one for each side of the chart. Got {segment_count}."
)


class InvalidButterflyChartSegmentsError(Exception):
    def __init__(self, *, segment_count: int):
        message = BUTTERFLY_SEGMENT_COUNT_ERROR_MESSAGE.format(
            segment_count=segment_count
        )
        super().__init__(message)


def generate_butterfly(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> go.Figure:
    """Generates a butterfly chart.

    Notes:
        A butterfly chart draws one horizontal bar per primary field
        value, for each of the two secondary category segments, mirrored
        on either side of a shared central axis. The primary field values
        therefore make up the categories of the y-axis, and can contain
        any number of values (eg. each age band of an age/sex chart).
        The first requested segment is drawn
        on the left hand side of the chart.

    Args:
        chart_generation_payload: The payload for the chart generation.

    Returns:
        The figure for the butterfly chart.

    Raises:
        `InvalidButterflyChartSegmentsError`: If the payload does not
            resolve to exactly 2 secondary category segments.

    """
    figure = go.Figure()
    settings = DualCategoryChartSettings(
        chart_generation_payload=chart_generation_payload,
    )

    categories, grouped = _group_plots_by_secondary_category(
        chart_generation_payload=chart_generation_payload,
    )

    if len(grouped) != BUTTERFLY_SIDES_COUNT:
        raise InvalidButterflyChartSegmentsError(segment_count=len(grouped))

    for index, (group, data) in enumerate(grouped.items()):
        is_left_hand_side = index == LEFT_HAND_SIDE_INDEX
        # Every trace is plotted against the same ordered list of
        # categories, so that both sides of the chart stay aligned
        # even when a segment has no data for a given category.
        values: list[float | None] = [
            data["values"].get(category) for category in categories
        ]
        mirrored_values = [
            None if value is None else -value if is_left_hand_side else value
            for value in values
        ]

        figure.add_trace(
            go.Bar(
                x=mirrored_values,
                y=categories,
                name=data["label"] or group,
                orientation="h",
                marker={
                    "color": data["colour"],
                },
                customdata=values,
            )
        )

    layout_args = settings.get_butterfly_chart_config(
        categories=categories,
    )
    figure.update_layout(**layout_args)

    return figure


def _group_plots_by_secondary_category(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> tuple[list[str], dict[str, dict]]:
    """Collapses the given plots into one group per secondary category value.

    Notes:
        Each plot represents a single primary field value
        for a single segment. Grouping them by the secondary
        category value gives one group per side of the chart,
        with each group holding one value per primary field value.

        A butterfly chart draws a single bar per primary field value
        per side, so each group maps a primary field value to a single
        value. Where a plot holds more than one data point for a
        category, such as when the underlying metric is sourced from
        timeseries data, the last recorded data point is used. This
        matches how the dual category tables and downloads reduce the
        same plots, keeping the chart consistent with them.

    Args:
        chart_generation_payload: The payload for the chart generation.

    Returns:
        A tuple of the ordered primary field values (the y-axis
        categories) and a dict keyed by the secondary category value,
        ordered so that the first requested segment comes first.

    """
    grouped: dict[str, dict] = {}
    categories: dict[str, None] = {}

    secondary_category = chart_generation_payload.secondary_category

    for plot in chart_generation_payload.plots:
        selected_colour: colour_scheme.RGBAChartLineColours = (
            colour_scheme.RGBAChartLineColours.get_colour(
                colour=plot.parameters.line_colour
            )
        )
        group = getattr(plot.parameters, secondary_category)
        group_data = grouped.setdefault(group, {"values": {}})

        for category, value in zip(
            plot.x_axis_values, plot.y_axis_values, strict=False
        ):
            categories[category] = None
            group_data["values"][category] = float(value)

        group_data["label"] = plot.parameters.label
        group_data["colour"] = selected_colour.stringified

    ordered_groups = _order_groups_by_requested_segments(
        grouped=grouped,
        secondary_field_values=chart_generation_payload.secondary_field_values,
    )

    return list(categories), ordered_groups


def _order_groups_by_requested_segments(
    *,
    grouped: dict[str, dict],
    secondary_field_values: list[str] | None,
) -> dict[str, dict]:
    """Re-orders the given groups to match the requested segment order.

    Notes:
        Plots which return no data are dropped before the chart is
        generated. Without this, the side of the chart which a segment
        is drawn on would depend on which segment happened to return
        data first, rather than the order it was requested in.

    Args:
        grouped: The groups keyed by secondary category value.
        secondary_field_values: The requested secondary category
            values, in the order they were requested.

    Returns:
        The groups, ordered by the requested segment order.

    """
    if not secondary_field_values:
        return grouped

    ordered_groups = {
        secondary_field_value: grouped[secondary_field_value]
        for secondary_field_value in secondary_field_values
        if secondary_field_value in grouped
    }
    # Defensive fallback, so that no group can be dropped
    # if it was not part of the requested segments
    for group, data in grouped.items():
        ordered_groups.setdefault(group, data)

    return ordered_groups
