from typing import Dict, List, Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import PlotData, PlotsCollection
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

    def generate_plots_for_table(self) -> List[Dict[str, str]]:
        """Create a list of plots from the request

        Returns:
            A list of dictionaries showing the plot data in tabular format

        """
        plots = self.plots_interface.build_plots_data()
        tabular_data = TabularData(plots=plots)

        return tabular_data.create_plots_in_tabular_format()


def generate_table(plots_collection: PlotsCollection) -> List[Dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `plots_collection` model

    Args:
        plots_collection: The requested table plots parameters
            encapsulated as a model

    Returns:
        The requested plots in tabular format

    Raises:
        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `new_cases_daily` is currently only available
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
