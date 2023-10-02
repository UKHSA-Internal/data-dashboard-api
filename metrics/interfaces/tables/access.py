from typing import Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import PlotsCollection
from metrics.domain.tables.generation import TabularData
from metrics.interfaces.plots.access import PlotsInterface
from metrics.interfaces.tables.validation import validate_each_requested_table_plot

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class TablesInterface:
    def __init__(
        self,
        plots_collection: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: Optional[PlotsInterface] = None,
    ):
        self.plots_collection = plots_collection

        self.plots_interface = plots_interface or PlotsInterface(
            plots_collection=self.plots_collection,
            core_time_series_manager=core_time_series_manager,
        )

    def _build_tabular_data_from_plots_data(self) -> TabularData:
        plots = self.plots_interface.build_plots_data()
        return TabularData(plots=plots)

    def generate_plots_for_table(self) -> list[dict[str, str]]:
        """Create a list of plots from the request

        Returns:
            A list of dictionaries showing the plot data in tabular format

        """
        tabular_data = self._build_tabular_data_from_plots_data()
        return tabular_data.create_plots_in_tabular_format()

    def generate_full_plots_for_table(self) -> list[dict[str, str]]:
        """Create a list of plots from the request

        Notes:
            This will create plots whereby each data point will be rendered.
            E.g. if a date-based plot is selected with a 1-year range,
            then 365 data points will be returned in the output.


        Returns:
            A list of dictionaries showing the plot data in tabular format

        """
        tabular_data = self._build_tabular_data_from_plots_data()
        return tabular_data.create_tabular_plots()


def generate_table(plots_collection: PlotsCollection) -> list[dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `plots_collection` model

    Args:
        plots_collection: The requested table plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `COVID-19_deaths_ONSByDay` is only available
            for the topic of `COVID-19`

        `DatesNotInChronologicalOrderError`: If a provided `date_to`
            is chronologically behind the provided `date_from`.
            E.g. date_from = datetime.datetime(2022, 10, 2)
                & date_to = datetime.datetime(2021, 8, 1)
            Note that if None is provided to `date_to`
            then this error will not be raised.

    """
    validate_each_requested_table_plot(plots_collection=plots_collection)

    tables_interface = TablesInterface(plots_collection=plots_collection)
    return tables_interface.generate_plots_for_table()


def generate_table_for_full_plots(
    plots_collection: PlotsCollection,
) -> list[dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `plots_collection` model

    Notes:
        This will create plots whereby each data point will be rendered.
        E.g. if a date-based plot is selected with a 1-year range,
        then 365 data points will be returned in the output.

    Args:
        plots_collection: The requested table plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `COVID-19_deaths_ONSByDay` is only available
            for the topic of `COVID-19`

        `DatesNotInChronologicalOrderError`: If a provided `date_to`
            is chronologically behind the provided `date_from`.
            E.g. date_from = datetime.datetime(2022, 10, 2)
                & date_to = datetime.datetime(2021, 8, 1)
            Note that if None is provided to `date_to`
            then this error will not be raised.

    """
    validate_each_requested_table_plot(plots_collection=plots_collection)

    tables_interface = TablesInterface(plots_collection=plots_collection)
    return tables_interface.generate_full_plots_for_table()


def generate_table_v3(plots_collection: PlotsCollection) -> list[dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `plots_collection` model

    Args:
        plots_collection: The requested table plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format
        which is structured as follows:
        >>>[{"column_value": "2022-01-01", "values": [{"label": "Plot1", "value": "10"}]]

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `COVID-19_deaths_ONSByDay` is only available
            for the topic of `COVID-19`

        `DatesNotInChronologicalOrderError`: If a provided `date_to`
            is chronologically behind the provided `date_from`.
            E.g. date_from = datetime.datetime(2022, 10, 2)
                & date_to = datetime.datetime(2021, 8, 1)
            Note that if None is provided to `date_to`
            then this error will not be raised.

    """
    tabular_data = generate_table(plots_collection=plots_collection)
    return _cast_generic_key_over_column_value(tabular_data=tabular_data)


def generate_table_v4(plots_collection: PlotsCollection) -> list[dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `plots_collection` model

    Args:
        plots_collection: The requested table plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format
        which is structured as follows:
        >>>[{"column_value": "2022-01-01", "values": [{"label": "Plot1", "value": "10"}]]

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `COVID-19_deaths_ONSByDay` is only available
            for the topic of `COVID-19`

        `DatesNotInChronologicalOrderError`: If a provided `date_to`
            is chronologically behind the provided `date_from`.
            E.g. date_from = datetime.datetime(2022, 10, 2)
                & date_to = datetime.datetime(2021, 8, 1)
            Note that if None is provided to `date_to`
            then this error will not be raised.

    """
    return generate_table_for_full_plots(plots_collection=plots_collection)


def _cast_generic_key_over_column_value(
    tabular_data: list[dict[str, str]]
) -> list[dict[str, str]]:
    for plot in tabular_data:
        keys = plot.keys()

        explicit_column_heading = next(x for x in keys if x != "values")

        column_value = plot.pop(explicit_column_heading)
        plot["reference"] = column_value

    return tabular_data
