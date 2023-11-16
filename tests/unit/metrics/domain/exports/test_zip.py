from unittest import mock

from _pytest.logging import LogCaptureFixture

from metrics.domain.exports.zip import write_data_to_zip


class TestWriteDataToZip:
    @mock.patch("metrics.domain.exports.zip.zipfile.ZipFile")
    def test_behaves_as_expected(
        self,
        spy_zipfile: mock.MagicMock,
    ):
        """
        Given a valid list of downloads is provided
        When the write_data_to_zip() method is called
        Then the zipfile.zipfile method is called once and
            the return value is of type io.BytesIO
        """
        # Given
        expected_csv_body = [
            "infectious_disease",
            "respiratory",
            "COVID-19",
            "Nation",
            "England",
            "COVID-19_deaths_ONSByDay",
            "all",
            "75+",
            "default",
            "2023",
            "2023-03-08",
            "2364",
        ]
        fake_downloads = [{"name": "chart_name", "content": expected_csv_body}]

        # When
        expected_zip_files = write_data_to_zip(downloads=fake_downloads)

        # Then
        spy_zipfile.assert_called_once()
        assert isinstance(expected_zip_files, bytes)

    def test_logs_failure(self, caplog: LogCaptureFixture):
        """
        Given an invalid list of downloads is provided
        When the write_data_to_zip() method is called
        Then a keyError exception is logged.
        """
        # Given
        expected_csv_body = [
            "infectious_disease",
            "respiratory",
            "COVID-19",
            "Nation",
            "England",
            "COVID-19_deaths_ONSByDay",
            "all",
            "75+",
            "default",
            "2023",
            "2023-03-08",
            "2364",
        ]
        fake_invalid_downloads = [
            {"wrong_key": "chart_name", "content": expected_csv_body}
        ]

        # When
        write_data_to_zip(downloads=fake_invalid_downloads)

        # Then
        expected_log = "Failed to write bulk_downloads to zip write stream"
        assert expected_log in caplog.text
