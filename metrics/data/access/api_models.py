from typing import Dict, List, Union


def filter_is_list(field_name: str) -> str:
    return field_name + "__in"


def filter_is_string(field_name: str) -> str:
    if field_name == "date_from":
        return "dt__gte"

    return field_name


def validate_filter_name(field_name: str, filter_value: Union[List[str], str]) -> str:
    if isinstance(filter_value, List):
        return filter_is_list(field_name=field_name)

    return filter_is_string(field_name=field_name)


def validate_plot_filter(
    possible_fields: List[str],
    plot: Dict[str, Union[List[str], str]],
) -> Dict[str, Union[List[str], str]]:
    query_filter = {}

    for field_name, filter_value in plot.items():
        if filter_value and field_name in possible_fields:
            validated_field_name = validate_filter_name(
                field_name=field_name, filter_value=filter_value
            )
            query_filter[validated_field_name] = filter_value

    return query_filter


def validate_query_filters(
    possible_fields: List[str],
    plots: List[Dict[str, Union[List[str], str]]],
) -> List[Dict[str, Union[List[str], str]]]:
    """
    Adjust a list of query parameters to cater for things like 'dates from' and for lists of values
      as well as removing empty parameters. eg 'geography': '',

    For example, given this plot
        [
            {
            'topic': 'Influenza',
            'metric': 'weekly_hospital_admissions_rate',
            'stratum': ['0_4, '25_29'],
            'geography': '',
            'geography_type': '',
            'chart_type': 'bar',
            'date_from': '2023-02-03'
            }
        ]

        Then.........

        This item:      'stratum': ['0_4', '25_29']
        Would become:   'stratum__in': ['0_4', '25_29']

        This item:      'date_from': '2023-02-03'
        Would become:   'dt__gte': '2023-02-03'

        These items:    'geography': '',
                        'geography_type': '',
        Would get removed as they're not an intended query (ie. we are not asking for all missing geographies)

        This item:      'chart_type': 'bar',
        Would get removed as it's not a query parameter

        These items:    'topic': 'Influenza',
                        'metric': 'weekly_hospital_admissions_rate',
        Would pass through this function unchanged as they are already valid query parameter syntax

    Args:
        The possible fields for this query
        A list of query parameters

    Returns:
        The list of query parameters in the required format
    """

    all_queries = []

    for plot in plots:
        all_queries.append(
            validate_plot_filter(possible_fields=possible_fields, plot=plot)
        )

    return all_queries
