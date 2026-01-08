import datetime
from collections.abc import Iterable
from decimal import Decimal
from typing import Self

from dateutil.relativedelta import relativedelta
from pydantic.main import Any, BaseModel

from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.common.utils import (
    ChartAxisFields,
    ChartTypes,
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.models.charts.common import BaseChartRequestParams


class PlotParameters(BaseModel):
    """Holds all the request information / parameters for an individual plot on a chart."""

    chart_type: str = ""
    topic: str
    metric: str
    stratum: str | None = ""
    geography: str | None = ""
    geography_type: str | None = ""
    sex: str | None = ""
    age: str | None = ""
    date_from: str | None = ""
    date_to: str | None = ""
    label: str | None = ""
    confidence_intervals: str | None = ""
    confidence_colour: str | None = ""
    line_colour: str | None = ""
    line_type: str | None = ""
    x_axis: str | None = ""
    y_axis: str | None = ""
    override_y_axis_choice_to_none: bool = False
    use_smooth_lines: bool = True
    use_markers: bool = False
    metric_value_ranges: Iterable[tuple[Decimal, Decimal]] | None = None
    theme: str = ""
    sub_theme: str = ""

    @property
    def metric_group(self) -> str:
        return extract_metric_group_from_metric(self.metric)

    @property
    def date_from_value(self) -> datetime.date:
        """Parses the `date_from` into a date object.
        Defaults to 1 year ago from the current date.

        Returns:
            `date` object representing the `date_from` string
                or a default of 1 year ago from the current date.

        """
        return make_date_from_string(date_from=self.date_from)

    @property
    def date_to_value(self) -> datetime.date | None:
        """Parses the 'date_to' into a date object.
            Defaults to today's date.

        Returns:
            'date' object representing the 'date_to' string
            or a default of today's date
        """
        return make_date_to_string(date_to=self.date_to)

    @property
    def x_axis_value(self) -> str:
        return ChartAxisFields.get_x_axis_value(name=self.x_axis)

    @property
    def y_axis_value(self) -> str | None:
        if self.override_y_axis_choice_to_none:
            return None
        return ChartAxisFields.get_y_axis_value(name=self.y_axis)

    def to_dict_for_query(self) -> dict[str, str]:
        """Returns a dict representation of the model used for the corresponding query.

        Notes:
            A number of fields are ommitted which would not be needed
            for a database query related to this plot.
            x_axis and y_axis fields are combined into `fields_to_export` list.

        Returns:
            Dict[str, str]: A dict representation of the model.
                Where the keys are the names of the fields
                and the values are the values of those fields.
                E.g.
                    >>> {"topic": "COVID-19", ...}

        """
        params = {
            "fields_to_export": [
                self.x_axis_value,
                self.y_axis_value,
                "upper_confidence",
                "lower_confidence",
            ],
            "metric": self.metric or "",
            "topic": self.topic or "",
            "stratum": self.stratum or "",
            "geography": self.geography or "",
            "geography_type": self.geography_type or "",
            "sex": self.sex or "",
            "age": self.age or "",
            "metric_value_ranges": self.metric_value_ranges or [],
        }

        if self.is_timeseries_data:
            params["fields_to_export"].append("in_reporting_delay_period")
            params["date_from"] = self.date_from_value
            params["date_to"] = self.date_to_value
            params["field_to_order_by"] = self.x_axis_value

        return params

    @property
    def is_headline_data(self) -> bool:
        return DataSourceFileType[self.metric_group].is_headline

    @property
    def is_timeseries_data(self) -> bool:
        return DataSourceFileType[self.metric_group].is_timeseries

    @property
    def line_colour_enum(self) -> RGBAChartLineColours:
        if self.line_colour:
            return RGBAChartLineColours.get_colour(colour=self.line_colour)

        if self.chart_type == ChartTypes.bar.value:
            return RGBAChartLineColours.BLUE

        return RGBAChartLineColours.BLACK


class ChartRequestParams(BaseChartRequestParams):
    """Holds all the request information / params for a chart in its entirety."""

    metric_group: str | None = None
    plots: list[PlotParameters]


class NoReportingDelayPeriodFoundError(Exception): ...


class ReportingDelayNotProvidedToPlotsError(Exception): ...


class PlotGenerationData(BaseModel):
    """Holds all the information needed to draw an individual plot, including the parameters and hydrated data."""

    parameters: PlotParameters
    x_axis_values: Any
    y_axis_values: Any
    additional_values: dict[str, Any] | None = {}
    latest_date: Any = None  # noqa: UP007

    @classmethod
    def create_from_parameters(
        cls, parameters: PlotParameters, aggregated_results: dict, latest_date: str
    ) -> Self:
        keys_to_exclude = [parameters.x_axis_value, parameters.y_axis_value]
        additional_values = {
            key: value
            for key, value in aggregated_results.items()
            if key not in keys_to_exclude
        }
        return cls(
            parameters=parameters,
            x_axis_values=aggregated_results[parameters.x_axis_value],
            y_axis_values=aggregated_results[parameters.y_axis_value],
            additional_values=additional_values,
            latest_date=latest_date,
        )

    @property
    def start_of_reporting_delay_period_index(self) -> int:
        """Fetches the index of the start of the reporting delay period

        Raises:
            `ReportingDelayNotProvidedToPlotsError`: If the
                reporting delay period was never provided
                to the `PlotsData` model
            `NoReportingDelayPeriodFoundError`: If there
                is no detectable reporting delay period.
                This can happen when all the booleans
                are returned as False.
                i.e. When a dataset does not yet
                support a reporting delay period.

        Returns:
            An integer representing the index of the
            first occurrence of `True` in the reporting
            delay periods. This can be used to draw the
            reporting delay period on charts.

        """
        try:
            reporting_delay_period_values = self.additional_values[
                "in_reporting_delay_period"
            ]
        except (KeyError, TypeError) as error:
            raise ReportingDelayNotProvidedToPlotsError from error

        for index, in_reporting_delay_period in enumerate(
            reporting_delay_period_values
        ):
            if in_reporting_delay_period is True:
                return index
        raise NoReportingDelayPeriodFoundError


class ChartGenerationPayload(BaseModel):
    """Holds all the information needed to draw a chart in its entirety, including params and data for each plot."""

    plots: list[PlotGenerationData]
    chart_width: int
    chart_height: int
    x_axis_title: str
    y_axis_title: str
    y_axis_minimum_value: Decimal = 0
    y_axis_maximum_value: Decimal | None = None
    legend_title: str | None = ""
    confidence_intervals: bool | None = False
    confidence_colour: str | None = ""


class CompletePlotData(BaseModel):
    """Data model to hold the parameters and the full-enriched queryset

    Notes:
        This is primarily used for instances in which
        the queryset is returned with full records
        as opposed to the `values_list` of the
        selected axes choices

    """

    parameters: PlotParameters
    queryset: Any


def get_date_n_months_ago_from_timestamp(
    *, datetime_stamp: datetime.datetime, number_of_months: int = 6
) -> datetime.date:
    """
    Get the 1st day of the month x months in the past

    Args:
        datetime_stamp: The datetime stamp to calculate from.
        number_of_months: the number of months to go back. Default 6

    Returns:
        A `date` object of the fist day of the month x months ago
    """

    n_months_ago: datetime.datetime = datetime_stamp - relativedelta(
        months=number_of_months
    )

    return datetime.datetime(
        year=n_months_ago.year, month=n_months_ago.month, day=1
    ).date()


def make_date_from_string(*, date_from: str | None) -> datetime.date:
    """Parses the `date_from` string into a date object. Defaults to 1 year ago from the current date.

    Args:
        date_from: A string representing the date in the format `%Y-%m-%d`
            E.g. "2022-10-01"

    Returns:
        `date` object representing the `date_from` string
            or a default of 1 year ago from the current date.

    """
    try:
        return datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        one_year = 12
        return get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime.date.today(), number_of_months=one_year
        )


def make_date_to_string(*, date_to: str | None) -> datetime.date:
    """Parse the 'date_to' string into a date object, defaults to today's date.

    Args:
        date_to: a string representing the date in teh form '%y-%m-%d'
            E.g. "2023-01-01"

    Returns:
        'date' object representing the 'date_to' string
            or a default of 1 year ago from the current date
    """
    try:
        return datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return datetime.date.today()
