from typing import List, Dict, Union


def create_filters(
    filterset_fields: List[str],
    plots: List[Dict[str, Union[List[str], str]]],
) -> List[Dict[str, Union[List[str], str]]]:
    """
    Adjust a Query Filter to cater for things like 'dates greater than' and lists of values
      as well as empty queries

    Args:
        The possible fields for this query
        A list of queries

    Returns:
        A Query Filter in the required format
    """

    all_queries = []

    for plot in plots:
        query_filter = {}

        for field, filter in plot.items():
            if filter and field in filterset_fields:
                if isinstance(filter, List):
                    query_filter[field + "__in"] = filter
                else:
                    # If filter is date_from then adjust query parameters accordingly
                    if field == "date_from":
                        query_filter["dt__gte"] = filter
                    else:
                        query_filter[field] = filter
        all_queries.append(query_filter)

    return all_queries
