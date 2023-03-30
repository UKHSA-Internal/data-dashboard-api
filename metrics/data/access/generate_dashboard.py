from enum import Enum
from typing import Dict, List, Union

from metrics.data.access.dashboard_metadata import virus_metadata
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.charts.line_with_shaded_section.information import get_metric_state


class Colour(Enum):
    red = -1
    neutral = 0
    green = 1


class ArrowDirection(Enum):
    up = -1
    neutral = 0
    down = 1


def format_cell(
    metric_name: str, metric_value: str, formatting: Dict[str, Union[str, bool]]
) -> str:
    """
    Purpose: format the incoming value.
    Arguments:  metric_name = Which metric this is
                metric_value -> The metric value to format
                formatting -> is a dictionary of actions to perform against metric_value
    Returns: The formatted metric_value or colour or arrow direction for the metric
    """
    try:
        for format_option, format_cell in formatting.items():
            if format_option == "absolute_number":  # Make it an absoloute number
                metric_value = (
                    str(abs(float(metric_value))) if format_cell else metric_value
                )
            elif (
                format_option == "number_format"
            ):  # Format the number (see ApplyFormatting enum )
                metric_value = str(format_cell).format(float(metric_value))
            elif format_option == "add_brackets":  # Add brackets around it
                metric_value = f"({metric_value})" if format_cell else metric_value
            else:
                if format_cell:
                    metric_state = get_metric_state(
                        change_in_metric_value=round(float(metric_value)),
                        metric_name=metric_name,
                    )

                    if format_option == "get_colour":  # Get the colour
                        metric_value = Colour(metric_state).name
                    elif format_option == "get_arrow":  # Get the arrow direction
                        metric_value = ArrowDirection(metric_state).name

        return metric_value

    except:
        return metric_value


def get_value_from_db(fields: List[str], filters: Dict[str, str]) -> Dict[str, str]:
    """
    Purpose: Pull back the required data from APITimeSeries model
    Arguments:  fields -> The fields that you want pulled back
                filter -> A dictionary of filters to apply to the request
    Returns: Dictionary of fieldnames & values that came back from the DB
    """

    try:
        return (
            APITimeSeries.objects.filter(**filters)
            .order_by("-dt")
            .values(*fields)
            .first()
        )

    except:  # trap for typos in the filters
        return {field: "no_value" for field in fields}


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
                k: v
                for k, v in tile.items()
                if k not in ["formatting", "filter", "fields"]
            }

            # TODO This chunk of code will need re-doing once we have more insight into future requirements
            # For now it only pulls back a metric OR a date. Lots more options/combinations may lie ahead
            metric_name: str = tile.get("filter", {}).get("metric")

            if metric_name:
                cell_vals: Dict[str:str] = get_value_from_db(
                    fields=tile.get("fields", ["metric_value"]),
                    filters=tile["filter"],
                )

                if cell_vals:
                    for cell_name, cell_value in cell_vals.items():
                        if cell_name == "dt":
                            result = cell_value.strftime("%-d %B %Y")
                            result_dict["secondary_container"] = result_dict[
                                "secondary_container"
                            ].replace("{}", result)
                        elif tile.get("formatting"):
                            result_dict["metric_value"]: str = format_cell(
                                metric_name=metric_name,
                                metric_value=str(cell_value),
                                formatting=tile.get("formatting"),
                            )
                        else:
                            result_dict["metric_value"]: str = str(cell_value)
                else:
                    if tile.get("fields", False):
                        result_dict["secondary_container"] = result_dict[
                            "secondary_container"
                        ].replace("{}", "no_value")
                    else:
                        result_dict["metric_value"] = "no_value"

            output_list.append(result_dict)

    return output_list
