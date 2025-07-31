import datetime
from unittest import mock

from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload
from metrics.interfaces.charts.subplot_charts.access import ChartsInterface, generate_chart_file

class TestChartsInterface:
    pass


class TestGenerateChartAsFile:
    @mock.patch.object(ChartsInterface, "write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_output")
    def test_delegates_call_for_writing_chart(
        self,
        spy_generate_chart_output: mock.MagicMock,
        spy_write_figure: mock.MagicMock,
        fake_chart_subplot_params: SubplotChartGenerationPayload,
    ):
        """
        Given a mock in place of a `SubplotChartGenerationPayload` model
        When `generate_chart_as_file` is called
        Then `write_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_subplot_collection = mock.Mock()
        mocked_subplots_collection.subplots_data = fake_chart_subplot_params

        # When
        generate_chart_file(chart_request_params=mocked_subplot_collection)

        # Then
        spy_write_figure.assert_called_once_with(
            figure=spy_generate_chart_output.figure.return_value.figure,
        )