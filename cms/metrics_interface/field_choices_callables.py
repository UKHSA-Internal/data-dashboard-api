"""
This file contains a series of functions which wrap instance of the `MetricsAPIInterface`.
These callables are then passed to the CMS fields.

This means that we don't need to create a new migration whenever a new record is added to that table.
Instead, the 1-off migration is pointed at this callable.
So Wagtail will pull the choices by invoking this function.

This shall ensure that the `choices` are populated from the database.
And allowing the CMS to provide the content creator with access to the `latest` data after the point of ingestion.
"""

from cms.metrics_interface import MetricsAPIInterface

LIST_OF_TWO_STRING_ITEM_TUPLES = list[tuple[str, str]]
GEOGRAPHY_TYPE_NAME_FOR_ALERTS = "Government Office Region"


def _build_two_item_tuple_choices(
    *, choices: list[str]
) -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    return [(choice, choice) for choice in choices]


def get_possible_axis_choices() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `chart axis` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new axis field is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of chart_types.
        Examples:
            [("geography", "geography"), ...]

    """
    return MetricsAPIInterface.get_chart_axis_choices()


def get_all_unique_metric_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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
            [("COVID-19_deaths_ONSByDay", "COVID-19_deaths_ONSByDay"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_unique_metric_names()
    )


def get_chart_types() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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


def get_chart_line_types() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `line_type` fields of the CMS blocks.

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
            [("SOLID", "SOLID"), ...]

    """
    return MetricsAPIInterface.get_chart_line_types()


def get_colours() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `colour` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of colours.
        Examples:
            [("BLUE", "BLUE"), ...]

    """
    return MetricsAPIInterface.get_colours()


def get_all_topic_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_topic_names()
    )


def get_a_list_of_all_topic_names():
    """Callable for the `topic` fields of the CMS blocks

    Notes:
        This callable wraps the `MetricAPIInterface` and is
        used to return all topic names as a list.

    Returns:
        A list of strings representing the topic names.
        Examples ["COVID-19", "Influenza"]
    """
    metrics_interface = MetricsAPIInterface()
    return list(metrics_interface.get_all_topic_names())


def get_all_unique_change_type_metric_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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
            [("COVID-19_headline_ONSdeaths_7DayChange",
              "COVID-19_headline_ONSdeaths_7DayChange"),
                ...
            ]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_unique_change_type_metric_names()
    )


def get_all_unique_percent_change_type_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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
            [("COVID-19_headline_ONSdeaths_7DayPercentChange",
              "COVID-19_headline_ONSdeaths_7DayPercentChange"),
                ...
            ]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_unique_percent_change_type_names()
    )


def get_all_stratum_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `stratum` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Stratum` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of stratum names.
        Examples:
            [("default", "default"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_stratum_names()
    )


def get_all_geography_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `geography` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Geography` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of geography names.
        Examples:
            [("England", "England"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_geography_names()
    )


def get_all_geography_names_and_codes_for_alerts() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """This field has been stubbed out to prevent the caller from preemptively referencing the `Geography` table"""
    return []


def get_all_geography_type_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `geography_type` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Geography` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of geography type names.
        Examples:
            [("Nation", "Nation"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_geography_type_names()
    )


def get_all_sex_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `sex` fields of the CMS blocks.

    Returns:
        A list of 2-item tuples of sex names.
        Examples:
            [("M", "M"), ("F", "F"), ...]

    """
    names = ["all", "f", "m"]
    return _build_two_item_tuple_choices(choices=names)


def get_all_age_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `age` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Age` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of sex names.
        Examples:
            [("40-44", "40-44"), ("45-54", "45-54"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(choices=metrics_interface.get_all_age_names())
