from typing import Dict, List, Union

from metrics.data.access.dashboard_metadata import virus_metadata
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.charts.line_with_shaded_section.information import (
    is_metric_improving,
)


def format_val(metric: str, num: str, formatting: Dict[str, Union[str, bool]]) -> str:
    """
    Purpose: format the incoming number
    Arguments:  metric = Which metric this is
                num -> The number to format
                formatting -> is a dictionary of actions to perform against num
    Returns: The formatted number or colour or arrow direction for the metric
    """

    try:
        for format_option, format_value in formatting.items():
            match format_option:
                case "absolute_number":  # Make it an absoloute number
                    num = str(abs(float(num))) if format_value else num
                case "number_format":  # Format the number (see ApplyFormatting enum )
                    num = str(format_value).format(float(num))
                case "add_brackets":  # Add brackets around it
                    num = f"({num})" if format_value else num
                case "get_colour":  # Get the colour
                    if format_value:
                        improving = is_metric_improving(
                            change_in_metric_value=int(float(num)),
                            metric_name=metric,
                        )
                        num = "green" if improving else "red"
                case "get_arrow":  # Get the arrow direction
                    if format_value:
                        num = "up" if float(num) > 0 else "down"

        return num

    except:
        return num


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

            metric: str = tile.get("filter", {}).get("metric")

            if metric:
                data_val: str = get_metric_value_from_db(filter=tile["filter"])
                result_dict["metric_value"]: str = format_val(
                    metric=metric,
                    num=str(data_val),
                    formatting=tile.get("formatting"),
                )

            output_list.append(result_dict)

    return output_list
