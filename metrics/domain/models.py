import datetime
from typing import Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from pydantic.main import Any, BaseModel


class PlotParameters(BaseModel):
    chart_type: str
    topic: str
    metric: str
    stratum: Optional[str]
    geography: Optional[str]
    geography_type: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    label: Optional[str] = ""
    line_colour: Optional[str] = ""
    line_type: Optional[str] = ""

    @property
    def topic_name(self) -> str:
        return self.topic

    @property
    def metric_name(self) -> str:
        return self.metric

    @property
    def geography_name(self) -> Optional[str]:
        return self.geography

    @property
    def geography_type_name(self) -> Optional[str]:
        return self.geography_type

    @property
    def stratum_name(self) -> Optional[str]:
        return self.stratum

    @property
    def date_from_value(self) -> datetime.date:
        """Parses the `date_from` into a date object.
        Defaults to 1 year ago from the current date.

        Returns:
            `date` object representing the `date_from` string
                or a default of 1 year ago from the current date.

        """
        return make_date_from_string(date_from=self.date_from)

    def to_dict_for_query(self) -> Dict[str, str]:
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
            "date_from": self.date_from_value,
        }


class PlotsCollection(BaseModel):
    plots: List[PlotParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]
    chart_width: int
    chart_height: int


class PlotsData(BaseModel):
    parameters: PlotParameters
    x_axis_values: Any
    y_axis_values: Any


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


def make_date_from_string(date_from: Optional[str]) -> datetime.date:
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
