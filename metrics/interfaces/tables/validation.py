from typing import Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, Metric
from metrics.domain.models import PlotParameters, PlotsCollection
from metrics.interfaces.plots.validation import PlotValidation

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_METRIC_MANAGER = Metric.objects


class TablesValidation:
    def __init__(
        self,
        plot_parameters: PlotParameters,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
        plot_validation: Optional[PlotValidation] = None,
    ):
        self.plot_parameters = plot_parameters
        self.core_time_series_manager = core_time_series_manager
        self.metric_manager = metric_manager

        self.plot_validation = plot_validation or PlotValidation(
            plot_parameters=plot_parameters,
            core_time_series_manager=core_time_series_manager,
            metric_manager=metric_manager,
        )

    def validate(self) -> None:
        """Validates the request against the contents of the db

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
        # Common validations delegated to the `PlotValidation` object
        self.plot_validation.validate()


def validate_each_requested_table_plot(plots_collection: PlotsCollection) -> None:
    """Validates the request plots against the contents of the db

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
    for plot_params in plots_collection.plots:
        validate_table_plot_parameters(plot_parameters=plot_params)


def validate_table_plot_parameters(plot_parameters: PlotParameters) -> None:
    """Validates the individual given `plot_parameters` against the contents of the db

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
    tables_validation = TablesValidation(plot_parameters=plot_parameters)
    tables_validation.validate()
