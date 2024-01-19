import operator
from collections.abc import Iterator
from functools import reduce

from django.db.models import Manager

from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.exports.csv import FIELDS
from metrics.domain.models import PlotsCollection
from metrics.domain.models.plots import CompletePlotData
from metrics.interfaces.plots.access import PlotsInterface

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class DownloadsInterface:
    def __init__(
        self,
        plots_collection: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: PlotsInterface | None = None,
    ):
        self.plots_collection = plots_collection

        self.plots_interface = plots_interface or PlotsInterface(
            plots_collection=self.plots_collection,
            core_time_series_manager=core_time_series_manager,
        )

    def build_downloads_data_from_plots_data(self) -> list[CompletePlotData]:
        complete_plots: list[
            CompletePlotData
        ] = self.plots_interface.build_plots_data_for_full_queryset()
        return merge_and_process_querysets(complete_plots=complete_plots)


def merge_and_process_querysets(
    complete_plots: list[CompletePlotData],
) -> CoreTimeSeriesQuerySet:
    """Merges the underlying querysets in the given `complete_plots`, orders and de-duplicates records too.

    Args:
        complete_plots: List of `CompletePlotData` models
            for which the querysets should be merged

    Returns:
        A single queryset containing the merged results
        in chronological order, starting from the latest records

    """
    all_querysets = _extract_querysets(complete_plots=complete_plots)
    queryset = merge_querysets(all_querysets=all_querysets)
    queryset = cast_queryset_for_desired_fields(queryset=queryset)
    return sort_queryset_according_to_x_axis(queryset=queryset)


def _extract_querysets(
    complete_plots: list[CompletePlotData],
) -> Iterator[CoreTimeSeriesQuerySet]:
    """Extracts the `queryset` from each individual `complete_plot`

    Args:
        complete_plots: The list of `CompletePlotData` models
            from which a queryset should be extracted from

    Returns:
        A generator of `CoreTimeSeriesQuerySet` objects

    """
    return (complete_plot.queryset for complete_plot in complete_plots)


def merge_querysets(
    all_querysets: Iterator[CoreTimeSeriesQuerySet],
) -> CoreTimeSeriesQuerySet:
    """Merges `all_querysets` into 1 queryset and removes duplicate records

    Args:
        all_querysets: An iterable of `CoreTimeSeriesQuerySet`

    Returns:
        A single queryset containing all the records
        from each queryset in `all_querysets`

    """
    merged_queryset = reduce(operator.or_, all_querysets)
    return merged_queryset.distinct()


def cast_queryset_for_desired_fields(
    queryset: CoreTimeSeriesQuerySet,
) -> CoreTimeSeriesQuerySet:
    """Casts the given `queryset` to the fields required for a downloadable export

    Args:
        queryset: The queryset to be parsed

    Returns:
        A queryset containing tuples of strings.
        Whereby each tuple represents 1 record
        And each string represents a value of a field

    """
    return queryset.values_list(*FIELDS.values(), named=True)


def sort_queryset_according_to_x_axis(
    queryset: CoreTimeSeriesQuerySet,
) -> CoreTimeSeriesQuerySet:
    """Sort the `queryset` according to the `x_axis`

    Args:
        queryset: The queryset to be sorted

    Returns:
        The sorted queryset.
        This will generally be sorted
        by the "date" value

    """
    return queryset.order_by("-date")


def get_downloads_data(chart_plots: PlotsCollection) -> CoreTimeSeriesQuerySet:
    """Gets the final queryset for the downloads export associated with the given `chart_plots`

    Args:
        chart_plots: The data model representing
            the requested plots for the downloads export

    Returns:
        A single queryset containing the merged results
        in chronological order, starting from the latest records

    """
    downloads_interface = DownloadsInterface(plots_collection=chart_plots)
    return downloads_interface.build_downloads_data_from_plots_data()
