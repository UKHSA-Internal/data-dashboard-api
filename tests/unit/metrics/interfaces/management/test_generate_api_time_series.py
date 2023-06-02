from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.generate_api_time_series"


class TestGenerateAPITimeSeries:
    @mock.patch(f"{MODULE_PATH}.generate_api_time_series")
    def test_delegates_call(self, spy_generate_api_time_series: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `generate_api_time_series`
        Then the call is delegated to the `generate_api_time_series()` function
        """
        # Given / When
        call_command("generate_api_time_series")

        # Then
        spy_generate_api_time_series.assert_called_once()
