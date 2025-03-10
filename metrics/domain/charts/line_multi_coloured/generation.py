import plotly

from metrics.domain.charts import chart_settings
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured import properties
from metrics.domain.charts.reporting_delay_period import add_reporting_delay_period
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import ChartGenerationPayload, PlotGenerationData


def create_multi_coloured_line_chart(
    *,
    chart_generation_payload: ChartGenerationPayload,
    figure: plotly.graph_objects.Figure | None = None,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload` model
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    figure = figure or plotly.graph_objects.Figure()
    chart_plots_data: list[PlotGenerationData] = chart_generation_payload.plots

    for plot_data in chart_plots_data:

        if plot_data.parameters.chart_type != "line_multi_coloured":
            continue

        line_plot: dict = create_line_plot(plot_data=plot_data)

        # Add line plot to the figure
        figure.add_trace(trace=line_plot)

    # Apply the typical styling for timeseries charts
    settings = chart_settings.ChartSettings(
        chart_generation_payload=chart_generation_payload
    )
    layout_args = settings.get_line_multi_coloured_chart_config()
    figure.update_layout(**layout_args)

    if settings.is_date_type_x_axis:
        add_reporting_delay_period(
            chart_plots_data=chart_plots_data,
            figure=figure,
        )

    return figure


def create_line_plot(*, plot_data: PlotGenerationData) -> dict:

    selected_colour = RGBAChartLineColours.get_colour(
        colour=plot_data.parameters.line_colour
    )
    selected_line_type = properties.ChartLineTypes.get_chart_line_type(
        line_type=plot_data.parameters.line_type
    )
    line_shape = "spline" if plot_data.parameters.use_smooth_lines else "linear"
    mode = "lines+markers" if plot_data.parameters.use_markers else "lines"
    legend = plot_data.parameters.label

    scatter = plotly.graph_objects.Scatter(
        x=plot_data.x_axis_values,
        y=plot_data.y_axis_values,
        mode=mode,
        line={
            "width": 2,
            "color": selected_colour.stringified,
            "dash": selected_line_type.value,
        },
        line_shape=line_shape,
        name=legend,
        showlegend=bool(legend),
    )
    return convert_graph_object_to_dict(graph_object=scatter)


def generate_chart_figure(
    *,
    chart_generation_payload: ChartGenerationPayload,
    figure: plotly.graph_objs.Figure | None,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload`
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    return create_multi_coloured_line_chart(
        chart_generation_payload=chart_generation_payload,
        figure=figure,
    )
