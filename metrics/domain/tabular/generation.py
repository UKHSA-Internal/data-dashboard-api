from collections import defaultdict
from typing import Dict, List, Tuple

from metrics.domain.models import ChartPlotData


def create_plots_in_tabular_format(
    chart_plots_data: List[ChartPlotData],
) -> List[Dict[str, str]]:
    """Creates the tabular output for the given chart plots

    Args:
        chart_plots_data: List of `ChartPlotData` models,
            where each model represents a requested plot.
    Returns:
        A list of dictionaries showing the chart plot data in tabular format
    """

    # Merge all the plots together by date
    plot_labels, combined_plots = combine_list_of_plots(
        chart_plots_data=chart_plots_data
    )

    # Output format depends on whether there is one plot or more than one
    if len(chart_plots_data) > 1:
        tabular_format = generate_multi_plot_output(
            plot_labels=plot_labels,
            combined_plots=combined_plots,
        )
    else:
        tabular_format = generate_single_plot_output(plot_data=combined_plots)

    return tabular_format


def combine_list_of_plots(
    chart_plots_data: List[ChartPlotData],
) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
    """Combines individual plots into a dictionary of dictionaries

    Args:
        chart_plots_data: List of `ChartPlotData` models,
            where each model represents a requested plot.
    Returns:
        1: The list of plot labels
        2: The individual plots combined into one dictionary of dictionaries
    """

    combined_plots: Dict[str, Dict[str, str]] = defaultdict(dict)
    plot_labels: List[str] = []

    for plot_num, plot in enumerate(chart_plots_data, 1):
        plot_label: str = plot.parameters.label or "Plot" + str(plot_num)
        plot_labels.append(plot_label)

        temp_dict = dict(zip(plot.x_axis, plot.y_axis))
        for k, v in temp_dict.items():
            combined_plots[str(k)].update({plot_label: str(v)})

    return plot_labels, combined_plots


def generate_multi_plot_output(
    plot_labels: List[str],
    combined_plots: Dict[str, Dict[str, str]],
):
    """Creates the tabular output for the given chart plots

    Args:
        plot_labels: List of Plot labels
        combined_plots: Combined list of individual plots
    Returns:
        A list of dictionaries showing the chart plots in tabular format
    """
    tabular_data = []

    for dt, plot_values in combined_plots.items():
        tabular_data.append(
            {
                "date": dt,
                "values": {
                    plot_label: plot_values.get(plot_label, "-")
                    for plot_label in plot_labels
                },
            }
        )

    return tabular_data


def generate_single_plot_output(plot_data: Dict[str, Dict[str, str]]):
    """Creates the tabular output for the given chart plot

    Args:
        plot_data: Data for the requested plot
    Returns:
        A list of dictionaries showing the chart plots in tabular format
    """
    tabular_data = []

    for dt, plot_value in plot_data.items():
        tabular_data.append({"date": dt, **plot_value})

    return tabular_data
