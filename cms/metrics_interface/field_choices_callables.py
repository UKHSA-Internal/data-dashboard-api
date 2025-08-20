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
DICT_OF_CHART_AXIS_AND_SUB_CATEGORIES = dict[str, list[str]]
GEOGRAPHY_TYPE_NAME_FOR_ALERTS = "Government Office Region"
DUAL_CHART_SECONDARY_CATEGORY_FILTER_LIST = ["metric", "date"]


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


def get_dual_chart_secondary_category_choices() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `dual chart secondary category` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        when a new choice is added to these choices.
        Instead, the 1-off migration is pointed at this callable.
        So wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of chart_secondary_category_choices.
        Examples:
            [("age", "age"), ...]
    """
    result = MetricsAPIInterface.get_chart_axis_choices()
    return [
        (choice, choice)
        for choice, choice in result
        if choice not in DUAL_CHART_SECONDARY_CATEGORY_FILTER_LIST
    ]


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


def get_all_timeseries_metric_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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
        choices=metrics_interface.get_all_timeseries_metric_names()
    )


def get_all_headline_metric_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
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
            [("COVID-19_headline_tests_7DayTotal", "COVID-19_headline_cases_7DayTotals"), ...

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_headline_metric_names()
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


def get_headline_chart_types() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `chart_type` fields of the CMS blocks
    for headline chart types.

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
            [("bar", "bar"), ...]

    """
    return MetricsAPIInterface.get_headline_chart_types()


def get_simplified_chart_types() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `chart_type` fields of the CMS blocks
    for simplified chart types.

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
            [("line_single_simplified", "line_single_simplified"), ...]

    """
    return MetricsAPIInterface.get_simplified_chart_types()


def get_dual_category_chart_types() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `chart_type` fields of the CMS blocks
    for dual category chart types.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of chart_types.
        Examples:
            [("stacked_bar", "stacked_bar"), ...]
    """
    return MetricsAPIInterface.get_dual_category_chart_types()


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


def get_all_theme_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `theme` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of theme names.
        Examples:
            [("Infectious_disease", "Infectious_disease"), ...]
    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_theme_names(),
    )


def get_all_sub_theme_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `sub_theme` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of sub_theme names.
        Examples:
            [("respiratory", "respiratory"), ...]
    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_sub_theme_names(),
    )


def get_all_unique_sub_theme_names() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable for the `choices` on the `sub_theme` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of unique sub_theme names.
        Examples:
            [("respiratory", "respiratory"), ...]
    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        choices=metrics_interface.get_all_unique_sub_theme_names(),
    )


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
        choices=metrics_interface.get_all_unique_topic_names()
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


def get_all_geography_names_and_codes_for_alerts() -> list:
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


def get_all_subcategory_choices() -> LIST_OF_TWO_STRING_ITEM_TUPLES:
    """Callable to return all category choices for initial load of dynamic CMS blocks.

    Notes:
        This callable returns a list combining the results of multiple callables
        that can be used for category choices in wagtail forms.
        For dynamic lists using javascript to update the form choices require that
        all possible choices are first loaded into the field `choices` when loading
        the form so that validation can work.

    Returns:
        A list of 2-item tuples for multiple attribute types
        Examples:
            [("40-44", "40-44"), ("45-54", "45-54"), ("m", "m"), ("f", "f"), ...]
    """
    return [
        *get_all_age_names(),
        *get_all_sex_names(),
        *get_all_stratum_names(),
        *get_all_geography_names(),
    ]


def get_all_geography_choices_grouped_by_type() -> (
    dict[str, LIST_OF_TWO_STRING_ITEM_TUPLES]
):
    """Callable to return all `geography` choices grouped by `geography_type`

    Notes:
        This callable returns a dict mapping each geography type to a list of 2-item tuples of
        associated geographies. That can be used for category choices in wagtail forms.

    Returns:
        A dict mapping each geography type to a list of 2-item tuples of of associated geographies.
        Examples:
            { "Nation": ["England", "England"], ... }
    """
    metrics_interface = MetricsAPIInterface()
    geography_types = [key for key, value in get_all_geography_type_names()]

    result = {}
    for geography_type in geography_types:
        result[geography_type] = _build_two_item_tuple_choices(
            choices=metrics_interface.get_all_geography_names_by_geography_type(
                geography_type_name=geography_type
            )
        )

    return result


def get_all_subcategory_choices_grouped_by_categories() -> (
    dict[
        str, LIST_OF_TWO_STRING_ITEM_TUPLES | dict[str, LIST_OF_TWO_STRING_ITEM_TUPLES]
    ]
):
    """Callable to return all subcategory choices groups by categories.

    Notes:
        This callable returns a list combining the results of multiple callables
        that can be used for subcategory choices in wagtail forms.
        This object is injected into the wagtail form via a `script` tag that can
        be consumed by JavaScript to update the options list based on a condition.

    Returns:
        A dictionary with values that contain a list of 2-item tuples for multiple attribute types
        Examples:
            { "age": ["40-44", "40-44"], "sex": ["m", "m"] ... }
    """
    return {
        "age": get_all_age_names(),
        "sex": get_all_sex_names(),
        "stratum": get_all_stratum_names(),
        "geography": get_all_geography_choices_grouped_by_type(),
    }
