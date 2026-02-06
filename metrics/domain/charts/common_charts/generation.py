import plotly.graph_objects

from metrics.domain.charts.chart_settings import single_category
from metrics.domain.charts.common_charts.plots.bar.plot import create_bar_plot
from metrics.domain.charts.common_charts.plots.line_multi_coloured.plot import (
    create_line_plot,
)
from metrics.domain.charts.reporting_delay_period import add_reporting_delay_period
from metrics.domain.common.utils import ChartTypes
from metrics.domain.models.plots import ChartGenerationPayload


def generate_chart_figure(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `values` as a `common` chart type

    Note:
        Common chart types include `bar` and `line_multi_coloured`, which can be combined
        into a single chart Eg: `bar_with_line`.

    Args:
        chart_generation_payload: Data required to generate the chart, including
        plot parameters.

    Returns:
        Plotly Figure object.
    """
    figure = plotly.graph_objects.Figure()
    settings = single_category.SingleCategoryChartSettings(
        chart_generation_payload=chart_generation_payload,
    )

    for plot in chart_generation_payload.plots:
        match plot.parameters.chart_type:
            case ChartTypes.bar.value:
                bar_plot = create_bar_plot(
                    plot_data=plot, chart_generation_payload=chart_generation_payload
                )
                figure.add_trace(trace=bar_plot)

            case ChartTypes.line_multi_coloured.value:
                line_plot = create_line_plot(plot_data=plot)
                figure.add_trace(trace=line_plot)

    if settings.is_date_type_x_axis:
        add_reporting_delay_period(
            chart_plots_data=chart_generation_payload.plots,
            figure=figure,
        )

    layout_args = settings.get_common_chart_config()
    figure.update_layout(**layout_args)

    return figure
