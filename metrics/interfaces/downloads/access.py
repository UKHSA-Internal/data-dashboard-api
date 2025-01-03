import operator
from collections.abc import Iterator
from functools import reduce

from django.db.models import Manager

from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.common.utils import (
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.exports.csv_output import FIELDS, HEADLINE_FIELDS
from metrics.domain.models import ChartRequestParams
from metrics.domain.models.plots import CompletePlotData
from metrics.interfaces.plots.access import PlotsInterface
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class DownloadsInterface:
    def __init__(
        self,
        *,
        plots_collection: ChartRequestParams,
        core_model_manager: CORE_MODEL_MANAGER_TYPE | None = None,
        plots_interface: PlotsInterface | None = None,
    ):
        self.plots_collection = plots_collection
        self.metric_group = extract_metric_group_from_metric(
            metric=self.plots_collection.plots[0].metric
        )
        self.core_model_manager = core_model_manager or self._get_core_model_manager()

        self.plots_interface = plots_interface or PlotsInterface(
            chart_request_params=self.plots_collection,
            core_model_manager=self.core_model_manager,
        )

    def _get_core_model_manager(self) -> Manager:
        """Returns `core_model_manager` based on the `metric_group

        Notes:
            The downloads interface can be used to generate downloads for
            either `CoreTimerseries` or `CoreHeadline` chart data.
            this function returns the Django manager to match the
            `metric_group` provided or defaults to `CoreTimeseries`
            if the `metric_type` is not provided.

        Returns:
            Manager: either `CoreTimeseries` or `CoreHeadline`
        """
        if DataSourceFileType[self.metric_group].is_timeseries:
            return DEFAULT_CORE_TIME_SERIES_MANAGER

        return DEFAULT_CORE_HEADLINE_MANAGER

    def build_downloads_data_from_plots_data(self) -> list[CompletePlotData]:
        complete_plots: list[CompletePlotData] = (
            self.plots_interface.build_plots_data_for_full_queryset()
        )

        if DataSourceFileType[self.metric_group].is_timeseries:
            return merge_and_process_timeseries_querysets(complete_plots=complete_plots)

        return merge_and_process_headline_querysets(complete_plots=complete_plots)


def merge_and_process_timeseries_querysets(
    *, complete_plots: list[CompletePlotData]
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
    queryset = merge_timeseries_querysets(all_querysets=all_querysets)
    queryset = cast_timeseries_queryset_for_desired_fields(queryset=queryset)

    return sort_queryset_according_to_x_axis(queryset=queryset)


def merge_and_process_headline_querysets(
    *, complete_plots: list[CompletePlotData]
) -> CoreHeadlineQuerySet:
    """Merges the underlying querysets in the given `complete_plots`

    Notes:
        the `CoreHeadline` does not require de-duplicating
        or sorting, only a single value per plot will be returned
        and the request should provide the order, not a date value.

    Args:
        complete_plots: List of `CompletePlotData` models
            for which the querysets should be merged

    Returns:
        A single queryset containing the merged results
    """
    all_querysets = _extract_querysets(complete_plots=complete_plots)
    queryset = merge_headline_querysets(all_querysets=all_querysets)
    return cast_headline_queryset_for_desired_fields(queryset=queryset)


def _extract_querysets(
    *,
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


def merge_timeseries_querysets(
    *, all_querysets: Iterator[CoreTimeSeriesQuerySet]
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


def merge_headline_querysets(
    *, all_querysets: Iterator[CoreHeadlineQuerySet]
) -> CoreHeadlineQuerySet:
    """Merges `all_querysets` into 1 query.

    Notes:
        The python operator.or_ function (bitwise OR)
        can be used to combine querysets of the same model.
        Its used in conjunction with `reduce()` function to
        combine multiple querysets from the `all_querysets` generator.

    Args:
        all_querysets: An iterable of `CoreHeadlineQuerySet`

    Returns:
        A single queryset containing all the records
        from each queryset in `all_querysets`
    """
    return reduce(operator.or_, all_querysets)


def cast_timeseries_queryset_for_desired_fields(
    *, queryset: CoreTimeSeriesQuerySet
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


def cast_headline_queryset_for_desired_fields(
    *, queryset: CoreHeadlineQuerySet
) -> CoreHeadlineQuerySet:
    """Casts the given `queryset` to the fields reqeust for a downloadable export
        of `CoreHeadline` data.

    Args:
        queryset: The queryset to be parsed

    Returns:
        A queryset contains tuples of strings.
        Whereby each tuple represents 1 records
        and each string reprensents a value of a field
    """
    return queryset.values_list(*HEADLINE_FIELDS.values(), named=True)


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


def get_downloads_data(*, chart_plots: ChartRequestParams) -> CoreTimeSeriesQuerySet:
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
