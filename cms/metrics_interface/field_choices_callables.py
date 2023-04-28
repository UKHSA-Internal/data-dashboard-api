from typing import List, Tuple

from cms.metrics_interface import MetricsAPIInterface

LIST_OF_TWO_STRING_TUPLES = List[Tuple[str, str]]


def _build_two_item_tuple_choices(choices: List[str]) -> LIST_OF_TWO_STRING_TUPLES:
    return [(choice, choice) for choice in choices]


def get_all_unique_metric_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `metric` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Metric` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of unique metric names.
        Examples:
            [("new_cases_daily", "new_cases_daily"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_unique_metric_names()
    )


def get_chart_types() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `chart_type` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of chart_types.
        Examples:
            [("line_with_shaded_section", "line_with_shaded_section"), ...]

    """
    return MetricsAPIInterface.get_chart_types()


def get_all_topic_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `topic` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Topic` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of topic names.
        Examples:
            [("COVID-19", "COVID-19"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(metrics_interface.get_all_topic_names())


def get_all_unique_change_type_metric_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `metric` fields of trend number CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Metric` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of change type metric names.
        Examples:
            [("new_cases_7days_change", "new_cases_7days_change"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_unique_change_type_metric_names()
    )


def get_all_unique_percent_change_type_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `percentage_metric` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Metric` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of change percent type metric names.
        Examples:
            [("new_cases_7days_change_percentage", "new_cases_7days_change_percentage"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_unique_percent_change_type_names()
    )


def get_all_stratum_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `stratum` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Topic` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of topic names.
        Examples:
            [("0_4", "0_4"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(metrics_interface.get_all_stratum_names())


def get_all_geography_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `geography` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Topic` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of topic names.
        Examples:
            [("England", "England"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(metrics_interface.get_all_geography_names())


def get_all_geography_type_names() -> LIST_OF_TWO_STRING_TUPLES:
    """Callable for the `choices` on the `geography_type` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Topic` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of topic names.
        Examples:
            [("Nation", "Nation"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_geography_type_names()
    )
