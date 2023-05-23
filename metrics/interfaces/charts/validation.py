import datetime
from typing import Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, Metric
from metrics.domain.utils import ChartTypes

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_METRIC_MANAGER = Metric.objects


class ChartTypeDoesNotSupportMetricError(Exception):
    ...


class MetricDoesNotSupportTopicError(Exception):
    ...


class DatesNotInChronologicalOrderError(Exception):
    ...


class ChartsRequestValidator:
    def __init__(
        self,
        topic_name: str,
        metric_name: str,
        chart_type: str,
        date_from: datetime.datetime,
        date_to: Optional[datetime.datetime] = None,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
    ):
        self.topic_name = topic_name
        self.metric_name = metric_name
        self.chart_type = chart_type
        self.date_from = date_from
        self.date_to = date_to
        self.core_time_series_manager = core_time_series_manager
        self.metric_manager = metric_manager

    def validate(self) -> None:
        """Validates the request against the contents of the db

        Returns:
            None

        Raises:
            `ChartTypeDoesNotSupportMetricError`: If the `metric` is not
                compatible for the required `chart_type`.
                E.g. A cumulative headline type number like `positivity_7days_latest`
                would not be viable for a line type (timeseries) chart.

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
        self._validate_series_type_chart_works_with_metric()
        self._validate_metric_is_available_for_topic()
        self._validate_dates()

    def _is_chart_series_type(self) -> bool:
        """Checks if the instance variable `chart_type` is of a timeseries type.

        Returns:
            bool: True if the `chart_type` can be used for timeseries data.
                False otherwise

        """
        if self.chart_type == ChartTypes.waffle.value:
            return False
        return True

    def _validate_series_type_chart_works_with_metric(self) -> None:
        requested_chart_is_series_type = self._is_chart_series_type()
        if not requested_chart_is_series_type:
            return

        metric_is_series_chart_compatible: bool = (
            self._does_metric_have_multiple_records()
        )
        if not metric_is_series_chart_compatible:
            raise ChartTypeDoesNotSupportMetricError(
                f"`{self.metric_name}` is not compatible with `{self.chart_type}` chart types"
            )

    def _does_metric_have_multiple_records(self) -> bool:
        """Checks the db if there are multiple associated `CoreTimeSeries` records.

        Returns:
            bool: True if there is more than 1 `CoreTimeSeries` record
                which match the criteria.
                False otherwise.

        """
        count: int = self.core_time_series_manager.get_count(
            topic_name=self.topic_name,
            metric_name=self.metric_name,
            date_from=self.date_from,
        )
        return count > 1

    def _validate_metric_is_available_for_topic(self) -> None:
        metric_is_topic_compatible: bool = self._is_metric_available_for_topic()

        if not metric_is_topic_compatible:
            raise MetricDoesNotSupportTopicError(
                f"`{self.topic_name}` does not have a corresponding metric of `{self.metric_name}`"
            )

    def _is_metric_available_for_topic(self) -> bool:
        """Checks the db if there are any `Metric` records for the `metric` and `topic`.

        Returns:
            bool: True if there are any `Metric` records
                which match the criteria.
                False otherwise.

        """
        return self.metric_manager.is_metric_available_for_topic(
            metric_name=self.metric_name,
            topic_name=self.topic_name,
        )

    def _are_dates_in_chronological_order(self) -> bool:
        """Checks if the `date_to` stamp is chronologically ahead of `date_from`

        Returns:
            bool: True if the date stamps are in the
                expected chronological order
                False otherwise.

        Raises:
            `TypeError`: If an invalid type is provided for either stamp
            i.e. if None is provided as `date_to`

        """
        return self.date_to > self.date_from

    def _validate_dates(self) -> None:
        """Checks if the `date_to` stamp is chronologically ahead of `date_from`

        Notes:
            If `None` is provided to either 1 or both
            of the date stamps, then this will return early
            and no further validation will be performed.
            This is to handle cases when the caller has
            specified a `date_from` but not a `date_to`.
            In that scenario, `date_to` is implicitly
            expect to be considered as the current date.

        Raises:
            `DatesNotInChronologicalOrderError`: If the date stamps
                are not in the correct expected chronological order

        """
        try:
            dates_in_chronological_order: bool = (
                self._are_dates_in_chronological_order()
            )
        except TypeError:
            return

        if not dates_in_chronological_order:
            raise DatesNotInChronologicalOrderError()

        return None
