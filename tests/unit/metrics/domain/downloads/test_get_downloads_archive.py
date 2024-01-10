import datetime
from unittest import mock

from metrics.domain.bulk_downloads.get_downloads_archive import (
    get_bulk_downloads_archive,
)

MODULE_PATH = "metrics.domain.bulk_downloads.get_downloads_archive"


class TestGetBulkDownloadsArchive:
    @mock.patch(f"{MODULE_PATH}.get_all_downloads")
    @mock.patch(f"{MODULE_PATH}.write_data_to_zip")
    def test_get_bulk_downloads_archive_delegates_calls_correctly(
        self,
        spy_write_data_to_zip: mock.MagicMock,
        spy_get_all_downloads: mock.MagicMock,
    ):
        """
        Given a fake file_format
        When the get_bulk_downloads_archive method is called
        Then the get_all_downloads crawler function is called
            and the write_data_to_zip export function is called.
        """
        # Given
        fake_file_format = "csv"

        # When
        get_bulk_downloads_archive(file_format=fake_file_format)

        # Then
        spy_get_all_downloads.assert_called_once()
        expected_downloads = spy_get_all_downloads.return_value
        spy_write_data_to_zip.assert_called_once_with(downloads=expected_downloads)

    @mock.patch(f"{MODULE_PATH}.get_all_downloads")
    @mock.patch(f"{MODULE_PATH}.write_data_to_zip")
    def test_get_bulk_downloads_archive_returns_filename_including_data(
        self,
        mocked_write_data_to_zip: mock.MagicMock,
        mocked_get_all_downloads: mock.MagicMock,
    ):
        """
        Given a fake file_format
        When the get_bulk_downloads_archive function is called
        Then a zip_file_name is return as part of the pay load that includes
            today's date
        """
        # Given
        fake_file_format = "csv"

        # When
        expected_zip_file = get_bulk_downloads_archive(file_format=fake_file_format)

        # Then
        expected_date: str = datetime.datetime.now().strftime("%Y-%m-%d")
        expected_zip_file_name = f"ukhsa_data_dashboard_downloads_{expected_date}.zip"
        assert expected_zip_file["zip_file_name"] == expected_zip_file_name

    @mock.patch(f"{MODULE_PATH}.get_all_downloads")
    @mock.patch(f"{MODULE_PATH}.write_data_to_zip")
    def test_get_bulk_downloads_archive_returns_zip_file_data(
        self,
        spy_write_data_to_zip: mock.MagicMock,
        mocked_get_all_downloads: mock.MagicMock,
    ):
        """
        Given a fake file_format
        When the get_bulk_downloads_archive function is called
        Then a zip_file_data list will be returned as art of the payload
        """
        # Given
        fake_file_format = "csv"

        # When
        expected_zip_file = get_bulk_downloads_archive(file_format=fake_file_format)

        # Then
        expected_zip_file_data = spy_write_data_to_zip.return_value
        assert expected_zip_file_data == expected_zip_file["zip_file_data"]
