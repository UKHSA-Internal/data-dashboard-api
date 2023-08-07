import datetime
from unittest import mock

import pytest

from metrics.domain.models.plots import (
    PlotParameters,
    get_date_n_months_ago_from_timestamp,
    make_date_from_string,
)
from metrics.domain.utils import ChartAxisFields

MODULE_PATH: str = "metrics.domain.models.plots"


class TestPlotParameters:
    mandatory_parameters = {
        "chart_type": "bar",
        "topic": "COVID-19",
        "metric": "COVID-19_deaths_ONSByDay",
    }
    optional_field_names = [
        "stratum",
        "geography",
        "geography_type",
        "sex",
        "age",
        "date_from",
        "date_to",
        "label",
        "line_colour",
        "line_type",
    ]

    def test_validates_successfully_when_optional_parameters_are_none(self):
        """
        Given a set of mandatory parameters and None for each optional field
        When an instance of the `PlotParameters` model is created
        Then a `ValidationError` is not raised
        """
        # Given
        optional_parameters_as_none = {
            field_name: None for field_name in self.optional_field_names
        }

        # When / Then
        PlotParameters(**self.mandatory_parameters, **optional_parameters_as_none)

    def test_validates_successfully_when_optional_parameters_are_empty_strings(self):
        """
        Given a set of mandatory parameters and an empty string for each optional field
        When an instance of the `PlotParameters` model is created
        Then a `ValidationError` is not raised
        """
        # Given
        optional_parameters_as_empty_strings = {
            field_name: "" for field_name in self.optional_field_names
        }

        # When / Then
        PlotParameters(
            **self.mandatory_parameters, **optional_parameters_as_empty_strings
        )

    def test_validates_successfully_when_optional_parameters_not_provided(self):
        """
        Given a set of mandatory parameters and no optional fields provided
        When an instance of the `PlotParameters` model is created
        Then a `ValidationError` is not raised
        """
        # Given
        optional_parameters = {}

        # When / Then
        PlotParameters(**self.mandatory_parameters, **optional_parameters)

    def test_to_dict_for_query(self, fake_chart_plot_parameters: PlotParameters):
        """
        Given a payload containing optional fields which do not relate
            directly to the corresponding query filters
        When `to_dict_for_query()` is called from an instance of the `PlotParameters` model
        Then the returned dict contains the expected key-value pairs only
        """
        # Given
        geography = "London"
        geography_type = "Nation"
        sex = "Female"
        age = "0_4"

        date_from = "2022-10-01"
        label = "0 to 4 years old"
        line_colour = "BLUE"
        line_type = "dash"

        fake_chart_plot_parameters.geography = geography
        fake_chart_plot_parameters.geography_type = geography_type
        fake_chart_plot_parameters.date_from = date_from
        fake_chart_plot_parameters.label = label
        fake_chart_plot_parameters.line_colour = line_colour
        fake_chart_plot_parameters.line_type = line_type
        fake_chart_plot_parameters.sex = sex
        fake_chart_plot_parameters.age = age

        # When
        dict_used_for_query: dict[
            str, str
        ] = fake_chart_plot_parameters.to_dict_for_query()

        # Then
        expected_dict_used_for_query = {
            "topic_name": fake_chart_plot_parameters.topic_name,
            "metric_name": fake_chart_plot_parameters.metric_name,
            "stratum_name": fake_chart_plot_parameters.stratum_name,
            "geography_name": fake_chart_plot_parameters.geography_name,
            "geography_type_name": fake_chart_plot_parameters.geography_type_name,
            "sex": fake_chart_plot_parameters.sex,
            "age": fake_chart_plot_parameters.age,
            "date_from": fake_chart_plot_parameters.date_from_value,
            "x_axis": ChartAxisFields[fake_chart_plot_parameters.x_axis].value,
            "y_axis": ChartAxisFields[fake_chart_plot_parameters.y_axis].value,
        }
        # `chart_type`, `label`, `line_colour`, `line_type` and `date_to` and are omitted
        assert dict_used_for_query == expected_dict_used_for_query

    def test_properties_return_correct_field_values(self):
        """
        Given a `PlotParameters` instance
        When the `_name` properties are called for
            `topic`, `metric`, `geography`, `geography_type` & `stratum`
        Then the correct values are returned
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "COVID-19_deaths_ONSByDay"
        geography_name = "London"
        geography_type_name = "Nation"
        stratum_name = "0_4"

        # When
        chart_plot_parameters = PlotParameters(
            topic=topic_name,
            metric=metric_name,
            geography=geography_name,
            geography_type=geography_type_name,
            stratum=stratum_name,
            chart_type="bar",
        )

        # Then
        assert chart_plot_parameters.topic_name == topic_name
        assert chart_plot_parameters.metric_name == metric_name
        assert chart_plot_parameters.geography_name == geography_name
        assert chart_plot_parameters.geography_type_name == geography_type_name

    @mock.patch(f"{MODULE_PATH}.make_date_from_string")
    def test_date_from_value_property_delegates_call(
        self,
        spy_make_date_from_string: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given a valid `PlotParameters` model
        When the `date_from_value` property is called
        Then the call is delegated to the `make_date_from_string()` function
        """
        # Given
        plot_parameters = valid_plot_parameters

        # When
        date_from_stamp = plot_parameters.date_from_value

        # Then
        spy_make_date_from_string.assert_called_once_with(
            date_from=plot_parameters.date_from
        )
        assert date_from_stamp == spy_make_date_from_string.return_value


class TestMakeDatetimeFromString:
    def test_returns_correct_value(self):
        """
        Given a valid date string in the format `%Y-%m-%d`
        When `make_datetime_from_string()` is called
        Then a `datetime.datetime` object is returned for the given date
        """
        # Given
        year = "2023"
        month = "01"
        day = "01"
        date_from = f"{year}-{month}-{day}"

        # When
        parsed_date_from = make_date_from_string(date_from=date_from)

        # Then
        assert parsed_date_from.year == int(year)
        assert parsed_date_from.month == int(month)
        assert parsed_date_from.day == int(day)

    @mock.patch(f"{MODULE_PATH}.get_date_n_months_ago_from_timestamp")
    def test_delegates_call_to_get_default_of_one_year_if_none_provided(
        self,
        spy_get_date_n_months_ago_from_timestamp: mock.MagicMock,
    ):
        """
        Given an input `date_from` of None
        When `make_datetime_from_string()` is called
        Then `get_date_n_months_ago_from_timestamp()` is called
            to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = None

        # When
        parsed_date_from = make_date_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value

    @mock.patch(f"{MODULE_PATH}.get_date_n_months_ago_from_timestamp")
    def test_delegates_call_to_get_default_of_one_year_if_empty_string_provided(
        self,
        spy_get_date_n_months_ago_from_timestamp: mock.MagicMock,
    ):
        """
        Given an input `date_from` of an empty string
        When `make_datetime_from_string()` is called
        Then `get_date_n_months_ago_from_timestamp()` is called
            to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = ""

        # When
        parsed_date_from = make_date_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value


class TestGetDateNMonthsAgoFromTimestamp:
    def test_for_timestamp_of_january(self):
        """
        Given a datetime stamp of January, and an arg to get the date 1 month ago
        When `get_date_n_months_ago_from_timestamp()` is called
        Then the 1st December of the previous year (1 month ago) is returned
        """
        # Given
        datetime_stamp = datetime.datetime(year=2023, month=1, day=15)
        number_of_months_ago = 1

        # When
        n_months_ago: datetime.datetime = get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime_stamp,
            number_of_months=number_of_months_ago,
        )

        # Then
        expected_month: int = 12
        expected_year: int = datetime_stamp.year - 1
        # The given timestamp is in Jan, so December of the previous should be returned
        assert n_months_ago.month == expected_month
        assert n_months_ago.day == 1
        assert n_months_ago.year == expected_year

    @pytest.mark.parametrize(
        "timestamp_month_number", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    )
    def test_for_timestamps_within_the_same_year(self, timestamp_month_number: int):
        """
        Given a datetime stamp of within a particular year, and an arg to get the date 1 month ago
        When `get_date_n_months_ago_from_timestamp()` is called
        Then the 1st of the previous month is returned
        """
        # Given
        datetime_stamp = datetime.datetime(
            year=2023, month=timestamp_month_number, day=15
        )
        number_of_months_ago = 1

        # When
        n_months_ago: datetime.datetime = get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime_stamp,
            number_of_months=number_of_months_ago,
        )

        # Then
        expected_month: int = datetime_stamp.month - 1
        assert n_months_ago.month == expected_month
        assert n_months_ago.day == 1
        assert n_months_ago.year == datetime_stamp.year
