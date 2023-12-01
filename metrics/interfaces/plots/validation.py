from metrics.domain.models import PlotParameters


class MetricDoesNotSupportTopicError(Exception):
    def __init__(self, topic_name: str, metric_name: str):
        message = (
            f"`{topic_name}` does not have a corresponding metric of `{metric_name}`"
        )
        super().__init__(message)


class DatesNotInChronologicalOrderError(Exception):
    def __init__(self, date_from: str, date_to: str):
        message = f"`{date_to}` is not a date later than `{date_from}`"
        super().__init__(message)


class PlotValidation:
    def __init__(self, plot_parameters: PlotParameters):
        self.plot_parameters = plot_parameters

    def validate(self) -> None:
        """Validates the request against the contents of the db

        Raises:
            `MetricDoesNotSupportTopicError`: If the `metric` is not
                compatible with the requested `topic`.
                E.g. `COVID-19_deaths_ONSByDay` metric is
                not available for the topic of `Influenza`

            `DatesNotInChronologicalOrderError`: If a provided `date_to`
                is chronologically behind the provided `date_from`.
                E.g. date_from = datetime.datetime(2022, 10, 2)
                    & date_to = datetime.datetime(2021, 8, 1)
                Note that if None is provided to `date_to`
                then this error will not be raised.

        """
        self._validate_dates()
        self._validate_metric_with_topic()

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
        return self.plot_parameters.date_to > self.plot_parameters.date_from

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
            raise DatesNotInChronologicalOrderError(
                date_from=self.plot_parameters.date_from,
                date_to=self.plot_parameters.date_to,
            )

    def _validate_metric_with_topic(self) -> None:
        """Checks if the `topic` and `metric` on the plot parameters are compatible

        Raises:
            `MetricDoesNotSupportTopicError`: If the
                `topic` and `metric` are not compatible

        """
        if self._metric_is_compatible_with_topic():
            return

        raise MetricDoesNotSupportTopicError(
            topic_name=self.plot_parameters.topic_name,
            metric_name=self.plot_parameters.metric_name,
        )

    def _metric_is_compatible_with_topic(self) -> bool:
        """Checks if the `topic` and `metric` on the plot parameters are compatible

        Returns:
            bool: True if the `topic` and `metric` are compatible,
                False otherwise

        """
        return (
            self.plot_parameters.topic_name.lower()
            in self.plot_parameters.metric_name.lower()
        )
