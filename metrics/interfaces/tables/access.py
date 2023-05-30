from typing import Dict, List, Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import PlotsCollection, PlotsData
from metrics.domain.tables.generation import create_plots_in_tabular_format
from metrics.interfaces.plots.access import PlotsInterface

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class TablesInterface:
    def __init__(
        self,
        chart_plots: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: Optional[PlotsInterface] = None,
    ):
        self.chart_plots = chart_plots

        self.plots_interface = plots_interface or PlotsInterface(
            plots_collection=self.chart_plots,
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
