from unittest import mock

from _pytest.logging import LogCaptureFixture

from metrics.domain.exports.zip import (
    write_data_to_zip,
    write_directory_to_write_stream,
)

MODULE_PATH = "metrics.domain.exports.zip"


class TestWriteDataToZip:
    @mock.patch(f"{MODULE_PATH}.zipfile.ZipFile")
    def test_write_directory_to_stream_behaves_as_expected(
        self,
        mocked_zip_writestr: mock.MagicMock,
    ):
        """
        Given a valid directory name and download_group.
        When the `write_directory_to_write_stream()` is called.
        Then `zipfile.writestr()` is called n times.
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
        fake_directory_name = "directory_name"
        fake_download_group = [
            {"name": "chart_one", "content": expected_csv_body},
            {"name": "chart_two", "content": expected_csv_body},
        ]

        # When
        write_directory_to_write_stream(
            directory_name=fake_directory_name,
            download_group=fake_download_group,
            zipf=mocked_zip_writestr,
        )

        # Then
        expected_calls = [
            mock.call("directory_name/chart_one", expected_csv_body),
            mock.call("directory_name/chart_two", expected_csv_body),
        ]
        mocked_zip_writestr.writestr.assert_has_calls(
            expected_calls,
            any_order=True,
        )

    @mock.patch(f"{MODULE_PATH}.zipfile.ZipFile")
    def test_write_directory_to_stream_logs_exception(
        self,
        mocked_zip_writestr: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given an invalid download group.
        When the `write_directory_to_write_stream()` is called.
        Then a KeyError is logged.
        """
        # Given
        fake_directory_name = "directory_name"
        fake_download_group = [
            {"wrong_key": "chart_one", "content": []},
        ]

        # When
        write_directory_to_write_stream(
            directory_name=fake_directory_name,
            download_group=fake_download_group,
            zipf=mocked_zip_writestr,
        )

        # Then
        expected_log = "Failed to create directory directory_name and its files."
        assert expected_log in caplog.text

    @mock.patch(f"{MODULE_PATH}.zipfile.ZipFile")
    @mock.patch(f"{MODULE_PATH}.write_directory_to_write_stream")
    def test_behaves_as_expected(
        self,
        spy_write_directory_to_write_stream: mock.MagicMock,
        spy_zipfile: mock.MagicMock,
    ):
        """
        Given a valid list of downloads is provided
        When the `write_data_to_zip()` method is called
        Then the zipfile.Zipfile is called once and the
            `write_directory_to_write_stream()` is called n times
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
        fake_downloads = [
            {
                "directory_name": "group one",
                "downloads": [
                    {"name": "chart_one", "content": expected_csv_body},
                    {"name": "chart_two", "content": expected_csv_body},
                ],
            },
            {
                "directory_name": "group two",
                "downloads": [
                    {"name": "chart_one", "content": expected_csv_body},
                    {"name": "chart_two", "content": expected_csv_body},
                ],
            },
        ]

        # When
        expected_zip_files = write_data_to_zip(downloads=fake_downloads)

        # Then
        spy_zipfile.assert_called_once()
        assert spy_write_directory_to_write_stream.call_count == 2
        assert isinstance(expected_zip_files, bytes)

    def test_logs_failure(self, caplog: LogCaptureFixture):
        """
        Given an invalid list of downloads is provided
        When the `write_data_to_zip()` method is called
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
            {
                "wrong_key": "name",
                "downloads": [
                    {"name": "chart_one", "content": expected_csv_body},
                    {"name": "chart_two", "content": expected_csv_body},
                ],
            }
        ]

        # When
        write_data_to_zip(downloads=fake_invalid_downloads)

        # Then
        expected_log = "Failed to write bulk downloads to zip write stream."
        assert expected_log in caplog.text
