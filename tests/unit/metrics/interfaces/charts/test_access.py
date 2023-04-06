from unittest import mock

from metrics.interfaces.charts.access import ChartsInterface, ChartTypes

MODULE_PATH = "metrics.interfaces.charts.access"


@mock.patch(f"{MODULE_PATH}.waffle.generate_chart_figure")
def test_generate_chart_figure_from_waffle_module_is_called(
    spy_waffle_generate_chart_figure,
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


@mock.patch(f"{MODULE_PATH}.line.generate_chart_figure")
def test_generate_chart_figure_from_line_module_is_called(
    spy_line_generate_chart_figure,
):
    """
    Given a requirement for a `simple_line_graph` chart
    When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
    Then the `generate_chart_figure()` function is called from the `simple_line_graph` module
    """
    # Given
    chart_type: str = ChartTypes.simple_line_graph.value
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
    spy_line_generate_chart_figure.assert_called_once()
    assert generated_chart_figure == spy_line_generate_chart_figure.return_value


@mock.patch(f"{MODULE_PATH}.line_with_shaded_section.generate_chart_figure")
def test_generate_chart_figure_from_line_with_shaded_section_module_is_called(
    spy_line_with_shaded_section_generate_chart_figure,
):
    """
    Given a requirement for a `line_with_shaded_section` chart
    When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
    Then the `generate_chart_figure()` function is called from the `line_with_shaded_section` module
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
    spy_line_with_shaded_section_generate_chart_figure.assert_called_once()
    assert (
        generated_chart_figure
        == spy_line_with_shaded_section_generate_chart_figure.return_value
    )
