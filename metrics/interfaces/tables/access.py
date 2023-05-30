from typing import Dict, List, Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import PlotsCollection, PlotsData
from metrics.domain.tables.generation import create_plots_in_tabular_format
from metrics.interfaces.charts.access import validate_each_requested_chart_plot
from metrics.interfaces.plots.access import PlotsInterface

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
        plots_data: List[PlotsData] = self.plots_interface.build_plots_data()

        return create_plots_in_tabular_format(
            tabular_plots_data=plots_data,
        )


def generate_table(plots_collection: PlotsCollection) -> List[Dict[str, str]]:
    """Validates and creates tabular output based off the parameters provided within the `chart_plots` model

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

    """
    validate_each_requested_chart_plot(chart_plots=plots_collection)

    tables_interface = TablesInterface(plots_collection=plots_collection)
    return tables_interface.generate_plots_for_table()
