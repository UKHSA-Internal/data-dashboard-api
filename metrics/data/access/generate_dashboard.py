"""
Code to fetch the data required for the Alpha version of the Dashboard

** This implementation is only a temporary solution intended for the Alpha release **

Main function is 'populate_dashboard' which requires a topic and optionally a metadata file
  which the function can iterate through and to produce the desired output
"""

import logging
from enum import Enum
from typing import Dict, List, Union

from metrics.data.access.dashboard_metadata import virus_metadata
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.charts.line_with_shaded_section.information import get_metric_state

logger = logging.getLogger(__name__)


class Colour(Enum):
    """The colour that the front-end should paint the box.
        The colour indicates whether the metric is improving or worsening

    Red: Getting worse
    Green: Improving
    Neutral: No change

    The direction (-1, 0, 1) is determined by get_metric_state
    """

    red = -1
    neutral = 0
    green = 1


class ArrowDirection(Enum):
    """The arrow direction that the front-end should display.
        Direction indicates whether the metric has gone up or down

    The direction (-1, 0, 1) is determined by get_arrow_direction
    """

    down = -1
    neutral = 0
    up = 1


def get_arrow_direction(metric_value: float) -> int:
    """
    Determine the arrow that the Front-end should draw

    Args:
        metric_value: The metric value

    Returns:
        -1: FE should draw a down arrow
        0: no arrow
        1: Draw an up arrow
    """

    if metric_value == 0:
        return 0

    return 1 if metric_value > 0 else -1


def format_cell(
    metric_name: str, metric_value: str, formatting: Dict[str, Union[str, bool]]
) -> str:
    """
    Format or use the incoming metric_value according to the supplied formatting dictionary.

    Args:
        metric_name: Name of the metric. Only used as a paramter for get_metric_state function
        metric_value: The metric value to either format or evaluate
        formatting: A dictionary of actions to perform against metric_value

           Supported formatting actions are:
            "absolute_number": Boolean. Display number as an absolute one
            "add_brackets": Boolean. Add brackets around the metric
            "number_format": See ApplyFormatting class in dashboard_metadata.
                            eg. display as an integer or to 1dp etc
            "get_colour": Boolean. Return the appropriate colour
                            Uses Colour enum and get_metric_state
            "get_arrow": Boolean. Return the appropriate arrow direction
                            Uses ArrowDirection enum and get_arrow_direction

    Returns:
        The formatted metric or the colour or arrow direction

    Raises:
        Logs the exception and returns the formatted metric up to the exception point
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
                    if format_option == "get_colour":  # Get the colour
                        metric_state = get_metric_state(
                            change_in_metric_value=float(metric_value),
                            metric_name=metric_name,
                        )
                        metric_value = Colour(metric_state).name

                    elif format_option == "get_arrow":  # Get the arrow direction
                        metric_direction = get_arrow_direction(
                            metric_value=float(metric_value)
                        )
                        metric_value = ArrowDirection(metric_direction).name

        return metric_value

    except:
        logger.exception("An exception occurred")
        return metric_value


def get_value_from_db(fields: List[str], filters: Dict[str, str]) -> Dict[str, str]:
    """
    Pull back the required data from APITimeSeries model

    Args:
        fields: The field(s) that you want pulled back from the model
        filter: A dictionary of filters to apply to the request

    Returns:
        Dictionary of fieldnames & values that came back from the DB

    Raises:
        Logs the exception and returns "no_value"
    """

    try:
        return (
            APITimeSeries.objects.filter(**filters)
            .order_by("-dt")
            .values(*fields)
            .first()
        )

    except:  # trap for typos in the filters
        logger.exception("An exception occurred")
        return {field: "no_value" for field in fields}


def populate_dashboard(
    topic: str,
    metadata: Dict[str, List[Dict[str, str]]] = virus_metadata,
) -> List[Dict[str, str]]:
    """
    Generate a dictionary of results by pulling data back from the APITimeSeries model

    Args:
        topic: The topic to use as a filter on the metadata dictionary
        metadata: The metadata dictionary

    Returns:
        A list of dictionaries of things to be displayed by the front-end
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
