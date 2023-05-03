from metrics.domain.charts.line_multi_coloured import properties
from metrics.domain.models import ChartPlotData, ChartPlotParameters


def test_get_label_from_plot_data_returns_stratum_when_available(
    fake_chart_plot_parameters: ChartPlotParameters,
):
    """
    Given a `ChartPlotData` model with params containing a `stratum`
    When `get_label_from_plot_data()` is called
    Then the `stratum` field value is returned
    """
    # Given
    stratum = "0_4"
    fake_chart_plot_parameters.stratum = stratum
    plot_data = ChartPlotData(parameters=fake_chart_plot_parameters, data=[])

    # When
    label: str = properties.get_label_from_plot_data(plot_data=plot_data)

    # Then
    assert label == stratum


def test_get_label_from_plot_data_creates_label_when_stratum_not_available(
    fake_chart_plot_parameters: ChartPlotParameters,
):
    """
    Given a `ChartPlotData` model with params without a `stratum` value
    When `get_label_from_plot_data()` is called
    Then a fallback label is created with the `topic` and `metric`
    """
    # Given
    stratum = ""
    fake_chart_plot_parameters.stratum = stratum
    plot_data = ChartPlotData(parameters=fake_chart_plot_parameters, data=[])

    # When
    label: str = properties.get_label_from_plot_data(plot_data=plot_data)

    # Then
    topic = plot_data.parameters.topic
    metric = plot_data.parameters.metric
    assert label == f"{topic}:{metric}"
