from typing import Dict, List, Union

from metrics.data.access.dashboard_metadata import virus_metadata
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.charts.line_with_shaded_section.information import (
    is_metric_improving,
)


def format_val(
    metric_name: str, metric_value: str, formatting: Dict[str, Union[str, bool]]
) -> str:
    """
    Purpose: format the incoming number
    Arguments:  metric_name = Which metric this is
                metric_value -> The metric value to format
                formatting -> is a dictionary of actions to perform against metric_value
    Returns: The formatted metric_value or colour or arrow direction for the metric
    """

    try:
        for format_option, format_value in formatting.items():
            if format_option == "absolute_number":  # Make it an absoloute number
                metric_value = (
                    str(abs(float(metric_value))) if format_value else metric_value
                )
            elif (
                format_option == "number_format"
            ):  # Format the number (see ApplyFormatting enum )
                metric_value = str(format_value).format(float(metric_value))
            elif format_option == "add_brackets":  # Add brackets around it
                metric_value = f"({metric_value})" if format_value else metric_value
            elif format_option == "get_colour":  # Get the colour
                if format_value:
                    improving = is_metric_improving(
                        change_in_metric_value=int(float(metric_value)),
                        metric_name=metric_name,
                    )
                    metric_value = "green" if improving else "red"
            elif format_option == "get_arrow":  # Get the arrow direction
                if format_value:
                    metric_value = "up" if float(metric_value) > 0 else "down"

        return metric_value

    except:
        return metric_value


def get_metric_value_from_db(filter: Dict[str, str]) -> str:
    """
    Purpose: Pull back the required data from APITimeSeries model
    Arguments:  filter -> A dictionary of filters to apply to the request
    Returns: The number which got pulled back
    """

    try:
        return (
            APITimeSeries.objects.filter(**filter).order_by("-dt").first().metric_value
        )

    except:  # trap for typos in the filter and for no data resulting in metric_value generating an exception
        return "no_value"


def populate_dashboard(
    topic: str,
    metadata: Dict[str, List[Dict[str, str]]] = virus_metadata,
) -> List[Dict[str, str]]:
    """
    Purpose: Generate a dictionary of results by pulling data back from the APITimeSeries model
    Arguments:  topic -> Filter metadata dictionary to just this topic
                metadata -> Virus metadata
    Returns: A list of dictionaries of things to be displayed by the front-end
    """
    output_list: List = []
    if metadata.get(topic):
        for tile in metadata[topic]:
            result_dict: Dict[str, str] = {
                k: v for k, v in tile.items() if k not in ["formatting", "filter"]
            }

            metric_name: str = tile.get("filter", {}).get("metric")

            if metric_name:
                data_val: str = get_metric_value_from_db(filter=tile["filter"])
                result_dict["metric_value"]: str = format_val(
                    metric_name=metric_name,
                    metric_value=str(data_val),
                    formatting=tile.get("formatting"),
                )

            output_list.append(result_dict)

    return output_list
