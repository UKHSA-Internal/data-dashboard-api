import datetime
from unittest import mock

from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import ChartsInterface, make_datetime_from_string

MODULE_PATH = "metrics.interfaces.charts.access"


@mock.patch(f"{MODULE_PATH}.waffle.generate_chart_figure")
def test_generate_chart_figure_from_waffle_module_is_called(
    spy_waffle_generate_chart_figure: mock.MagicMock,
):
    """
    Given a requirement for a `waffle` chart
    When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
    Then the `generate_chart_figure()` function is called from the `waffle` module
    """
    # Given
    chart_type: str = ChartTypes.waffle.value
    charts_interface = ChartsInterface(
        chart_type=chart_type,
        topic=mock.Mock(),
        metric=mock.Mock(),
        date_from=mock.Mock(),
        core_time_series_manager=mock.Mock(),
    )

    # When
    generated_chart_figure = charts_interface.generate_chart_figure()

    # Then
    spy_waffle_generate_chart_figure.assert_called_once()
    assert generated_chart_figure == spy_waffle_generate_chart_figure.return_value


@mock.patch.object(ChartsInterface, "generate_simple_line_chart")
def test_generate_chart_figure_from_line_module_is_called(
    spy_generate_simple_line_chart_method: mock.MagicMock,
):
    """
    Given a requirement for a `simple_line_graph` chart
    When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
    Then the call is delegated to the `generate_simple_line_chart()` method
    """
    # Given
    chart_type: str = ChartTypes.simple_line.value
    charts_interface = ChartsInterface(
        chart_type=chart_type,
        topic=mock.Mock(),
        metric=mock.Mock(),
        date_from=mock.Mock(),
        core_time_series_manager=mock.Mock(),
    )

    # When
    generated_chart_figure = charts_interface.generate_chart_figure()

    # Then
    spy_generate_simple_line_chart_method.assert_called_once()
    assert generated_chart_figure == spy_generate_simple_line_chart_method.return_value


@mock.patch.object(ChartsInterface, "generate_line_with_shaded_section_chart")
def test_generate_chart_figure_from_line_with_shaded_section_module_is_called(
    spy_generate_line_with_shaded_section_chart: mock.MagicMock,
):
    """
    Given a requirement for a `line_with_shaded_section` chart
    When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
    Then the call is delegated to the `generate_line_with_shaded_section_chart()` method
    """
    # Given
    chart_type: str = ChartTypes.line_with_shaded_section.value
    charts_interface = ChartsInterface(
        chart_type=chart_type,
        topic=mock.Mock(),
        metric=mock.Mock(),
        date_from=mock.Mock(),
        core_time_series_manager=mock.Mock(),
    )

    # When
    generated_chart_figure = charts_interface.generate_chart_figure()

    # Then
    spy_generate_line_with_shaded_section_chart.assert_called_once()
    assert (
        generated_chart_figure
        == spy_generate_line_with_shaded_section_chart.return_value
    )


def test_get_timeseries_calls_core_time_series_manager_with_correct_args():
    """
    Given a `CoreTimeSeriesManager`
    When `get_timeseries()` is called from an instance of `ChartsInterface`
    Then the correct method is called from `CoreTimeSeriesManager` to retrieve the timeseries
    """
    # Given
    spy_core_time_series_manager = mock.Mock()
    mocked_topic = mock.Mock()
    mocked_metric = mock.Mock()
    mocked_date_from = mock.Mock()
    charts_interface = ChartsInterface(
        chart_type=mock.Mock(),
        topic=mocked_topic,
        metric=mocked_metric,
        date_from=mocked_date_from,
        core_time_series_manager=spy_core_time_series_manager,
    )

    # When
    timeseries = charts_interface.get_timeseries()

    # Then
    assert (
        timeseries
        == spy_core_time_series_manager.by_topic_metric_for_dates_and_values.return_value
    )
    spy_core_time_series_manager.by_topic_metric_for_dates_and_values.assert_called_once_with(
        topic=mocked_topic,
        metric_name=mocked_metric,
        date_from=mocked_date_from,
    )


def test_is_metric_series_type_data():
    """
    Given a `CoreTimeSeriesManager` and an incompatible metric/chart_type combination
    When `is_metric_series_type_data()` is called from an instance of `ChartsInterface`
    Then the correct method is called from `CoreTimeSeriesManager` to retrieve the timeseries
    """
    # Given
    spy_core_time_series_manager = mock.Mock()
    mocked_topic = mock.Mock()
    mocked_metric = mock.Mock()
    mocked_date_from = mock.Mock()
    charts_interface = ChartsInterface(
        chart_type=mock.Mock(),
        topic=mocked_topic,
        metric=mocked_metric,
        date_from=mocked_date_from,
        core_time_series_manager=spy_core_time_series_manager,
    )

    # When
    timeseries = charts_interface.get_timeseries()

    # Then
    assert (
        timeseries
        == spy_core_time_series_manager.by_topic_metric_for_dates_and_values.return_value
    )
    spy_core_time_series_manager.by_topic_metric_for_dates_and_values.assert_called_once_with(
        topic=mocked_topic,
        metric_name=mocked_metric,
        date_from=mocked_date_from,
    )


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
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        assert type(parsed_date_from) == datetime.datetime
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
        Then `get_date_n_months_ago_from_timestamp()` is called to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = None

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

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
        Then `get_date_n_months_ago_from_timestamp()` is called to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = ""

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value
