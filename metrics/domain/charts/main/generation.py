from plotly.graph_objs import Figure

from metrics.domain.charts import chart_settings
from metrics.domain.charts.bar.generation import create_bar_plot
from metrics.domain.charts.line_multi_coloured.generation import create_line_plot
from metrics.domain.charts.reporting_delay_period import add_reporting_delay_period
from metrics.domain.common.utils import ChartTypes
from metrics.domain.models import ChartGenerationPayload


def generate_chart_figure(*, chart_generation_payload: ChartGenerationPayload):
    figure = Figure()
    settings = chart_settings.ChartSettings(
        chart_generation_payload=chart_generation_payload
    )

    for plot in chart_generation_payload.plots:
        match plot.parameters.chart_type:
            case ChartTypes.bar.value:
                bar_plot = create_bar_plot(plot_data=plot)
                figure.add_trace(trace=bar_plot)
                if settings.is_date_type_x_axis:
                    add_reporting_delay_period(
                        chart_plots_data=plot,
                        figure=figure,
                    )

            case ChartTypes.line_multi_coloured.value:
                line_multi_coloured_plot = create_line_plot(plot_data=plot)
                figure.add_trace(trace=line_multi_coloured_plot)
                if settings.is_date_type_x_axis:
                    add_reporting_delay_period(
                        chart_plots_data=plot,
                        figure=figure,
                    )


    layout_args = settings.get_bar_chart_config()
    figure.update_layout(**layout_args)

    return figure
