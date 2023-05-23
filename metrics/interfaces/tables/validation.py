import datetime
from typing import Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, Metric

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_METRIC_MANAGER = Metric.objects


class MetricDoesNotSupportTopicError(Exception):
    ...


class DatesNotInChronologicalOrderError(Exception):
    ...


class TablesRequestValidator:
    def __init__(
        self,
        topic: str,
        metric: str,
        date_from: datetime.datetime,
        date_to: Optional[datetime.datetime] = None,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
    ):
        self.topic = topic
        self.metric = metric
        self.date_from = date_from
        self.date_to = date_to
        self.core_time_series_manager = core_time_series_manager
        self.metric_manager = metric_manager

    def validate(self) -> None:
        """Validates the request against the contents of the db

        Returns:
            None

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
        self._validate_metric_is_available_for_topic()
        self._validate_dates()

    def _is_metric_available_for_topic(self) -> bool:
        """Checks the db if there are any `Metric` records for the `metric` and `topic`.

        Returns:
            bool: True if there are any `Metric` records
                which match the criteria.
                False otherwise.

        """
        return self.metric_manager.is_metric_available_for_topic(
            metric_name=self.metric,
            topic_name=self.topic,
        )

    def _validate_metric_is_available_for_topic(self) -> None:
        metric_is_topic_compatible: bool = self._is_metric_available_for_topic()

        if not metric_is_topic_compatible:
            raise MetricDoesNotSupportTopicError(
                f"`{self.topic}` does not have a corresponding metric of `{self.metric}`"
            )

    def _does_metric_have_multiple_records(self) -> bool:
        """Checks the db if there are multiple associated `CoreTimeSeries` records.

        Returns:
            bool: True if there is more than 1 `CoreTimeSeries` record
                which match the criteria.
                False otherwise.

        """
        count: int = self.core_time_series_manager.get_count(
            topic=self.topic,
            metric_name=self.metric,
            date_from=self.date_from,
        )
        return count > 1

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
