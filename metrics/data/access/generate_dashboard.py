from typing import Dict, List, Union

from metrics.data.access.dashboard_metadata import virus_metadata
from metrics.data.models.api_models import APITimeSeries


def format_val(num: str, formatting: Dict[str, Union[str, bool]]) -> str:
    """
    Purpose: format the incoming number
    Arguments:  num -> The number to format
                formatting -> is a dictionary of actions to perform against num
                              currently, only formatting and whether
                              to add brackets or not is supported
    Returns: The formatted number
    """

    try:
        if formatting:
            result = str(formatting["number_format"]).format(float(num))
            return f"({result})" if formatting.get("add_brackets", False) else result
        return num

    except:
        return num


def get_value_from_db(filter: Dict[str, str]) -> str:
    """
    Purpose: Pull back the required data from APITimeSeries model
    Arguments:  filter -> A dictionary of filters to apply to the request
    Returns: The number which got pulled back
    """

    try:
        return (
            APITimeSeries.objects.filter(**filter).order_by("-dt").first().metric_value
        )

    except:
        return "no_value"


def populate_dashboard(
    topic: str,
    metadata: Dict[str, List[Dict[str, str]]] = virus_metadata,
) -> List[Dict[str, str]]:
    """
    Purpose: Generate a dictionary of results by pulling data back from the APITimeSeries model
    Arguments:  topic -> Filter metadata dictionary to just this topic
                metadata -> Virus metadata
    Returns: A dictionary of things to be displayed by the front-end
    """
    output_list: List = []
    if metadata.get(topic):
        for tile in metadata[topic]:
            result_dict: Dict[str, str] = {
                k: v for k, v in tile.items() if k not in ["formatting", "filter"]
            }

            data_val: str = None
            if tile.get("filter", {}).get("metric"):
                data_val: str = get_value_from_db(filter=tile["filter"])

            if data_val:
                result_dict["metric_value"] = format_val(
                    num=str(data_val), formatting=tile.get("formatting")
                )

            output_list.append(result_dict)

    return output_list
