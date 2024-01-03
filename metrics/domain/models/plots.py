import datetime
from typing import Literal

from dateutil.relativedelta import relativedelta
from pydantic.main import Any, BaseModel

from metrics.domain.utils import ChartAxisFields


class PlotParameters(BaseModel):
    chart_type: str
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
    line_colour: str | None = ""
    line_type: str | None = ""
    x_axis: str | None = ""
    y_axis: str | None = ""
    override_y_axis_choice_to_none: bool = False

    @property
    def topic_name(self) -> str:
        return self.topic

    @property
    def metric_name(self) -> str:
        return self.metric

    @property
    def geography_name(self) -> str | None:
        return self.geography

    @property
    def geography_type_name(self) -> str | None:
        return self.geography_type

    @property
    def stratum_name(self) -> str | None:
        return self.stratum

    @property
    def age_name(self) -> str | None:
        return self.age

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

        Returns:
            Dict[str, str]: A dict representation of the model.
                Where the keys are the names of the fields
                and the values are the values of those fields.
                E.g.
                    >>> {"topic_name": "COVID-19", ...}

        """
        return {
            "metric_name": self.metric_name or "",
            "topic_name": self.topic_name or "",
            "stratum_name": self.stratum_name or "",
            "geography_name": self.geography_name or "",
            "geography_type_name": self.geography_type_name or "",
            "sex": self.sex or "",
            "age": self.age or "",
            "date_from": self.date_from_value,
            "date_to": self.date_to_value,
            "x_axis": self.x_axis_value,
            "y_axis": self.y_axis_value,
        }


class PlotsCollection(BaseModel):
    plots: list[PlotParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]
    chart_width: int
    chart_height: int
    x_axis: str
    y_axis: str


class PlotData(BaseModel):
    parameters: PlotParameters
    x_axis_values: Any
    y_axis_values: Any
    latest_date: Any = None  # noqa: UP007


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
    datetime_stamp: datetime.datetime, number_of_months: int = 6
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


def make_date_from_string(date_from: str | None) -> datetime.date:
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


def make_date_to_string(date_to: str | None) -> datetime.date:
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
