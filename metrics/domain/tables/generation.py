import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from metrics.domain.models import PlotsData


def create_plots_in_tabular_format(
    tabular_plots_data: List[PlotsData],
) -> List[Dict[str, str]]:
    """Creates the tabular output for the given plots

    Args:
        tabular_plots_data: List of `TabularPlotData` models,
            where each model represents a requested plot.

    Returns:
        A list of dictionaries showing the plot data in tabular format

    """
    # Merge all the plots together by date
    plot_labels, combined_plots = combine_list_of_plots(
        tabular_plots_data=tabular_plots_data
    )

    # Create output in required format
    tabular_format = generate_multi_plot_output(
        plot_labels=plot_labels,
        combined_plots=combined_plots,
    )

    return tabular_format


def get_last_day_of_month(dt: datetime.date) -> datetime.date:
    next_month = dt.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


def combine_list_of_plots(
    tabular_plots_data: List[PlotsData],
) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
    """Combines individual plots into a dictionary of dictionaries

    Args:
        tabular_plots_data: List of `TabularPlotData` models,
            where each model represents a requested plot.

    Returns:
        1: The list of plot labels
        2: The individual plots combined into one dictionary of dictionaries

    """
    combined_plots: Dict[str, Dict[str, str]] = defaultdict(dict)
    plot_labels: List[str] = []

    for plot_num, plot in enumerate(tabular_plots_data, 1):
        plot_label: str = plot.parameters.label or "Plot" + str(plot_num)
        plot_labels.append(plot_label)

        temp_dict = dict(zip(plot.x_axis_values, plot.y_axis_values))
        for k, v in temp_dict.items():
            month_end = str(get_last_day_of_month(k))
            combined_plots[month_end].update({plot_label: str(v)})

    return plot_labels, combined_plots


def generate_multi_plot_output(
    plot_labels: List[str],
    combined_plots: Dict[str, Dict[str, str]],
):
    """Creates the tabular output for the given plots

    Args:
        plot_labels: List of Plot labels
        combined_plots: Combined list of individual plots

    Returns:
        A list of dictionaries showing the plots in tabular format

    """
    tabular_data = []

    for dt, plot_values in sorted(combined_plots.items()):
        tabular_data.append(
            {
                "date": dt,
                "values": [
                    {"label": plot_label, "value": plot_values.get(plot_label)}
                    for plot_label in plot_labels
                ],
            }
        )

    return tabular_data
