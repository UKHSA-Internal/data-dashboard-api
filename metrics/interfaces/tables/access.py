from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import PlotsCollection
from metrics.domain.tables.generation import TabularData
from metrics.interfaces.plots.access import PlotsInterface

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class TablesInterface:
    def __init__(
        self,
        *,
        plots_collection: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: PlotsInterface | None = None,
    ):
        self.plots_collection = plots_collection

        self.plots_interface = plots_interface or PlotsInterface(
            plots_collection=self.plots_collection,
            core_model_manager=core_time_series_manager,
        )

    def _build_tabular_data_from_plots_data(self) -> TabularData:
        plots = self.plots_interface.build_plots_data()
        return TabularData(plots=plots)

    def generate_full_plots_for_table(self) -> list[dict[str, str]]:
        """Create a list of plots from the request

        Notes:
            This will create plots whereby each data point will be rendered.
            E.g. if a date-based plot is selected with a 1-year range,
            then 365 data points will be returned in the output.


        Returns:
            A list of dictionaries showing the plot data in tabular format

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        tabular_data = self._build_tabular_data_from_plots_data()
        return tabular_data.create_tabular_plots()


def generate_table_for_full_plots(
    *,
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
        `InvalidPlotParametersError`: If an underlying
            validation check has failed.
            This could be because there is
            an invalid topic and metric selection.
            Or because the selected dates are not in
            the expected chronological order.
        `DataNotFoundForAnyPlotError`: If no plots
            returned any data from the underlying queries
    """
    tables_interface = TablesInterface(plots_collection=plots_collection)
    return tables_interface.generate_full_plots_for_table()
