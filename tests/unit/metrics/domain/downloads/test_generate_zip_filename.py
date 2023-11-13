import datetime

from metrics.domain.bulk_downloads.get_downloads_archive import generate_zip_filename


class TestGenerateZipFilename:
    def test_generate_filename_includes_todays_date(self):
        """
        Given a fake date.
        When the generate_zip_filename() method is called.
        Then a string is returned with the expected date as its suffix.
        """
        # Given
        fake_date: str = datetime.datetime.now().strftime("%Y-%m-%d")

        # When
        expected_filename = generate_zip_filename()

        # Then
        assert f"ukhsa_data_dashboard_downloads_{fake_date}.zip" == expected_filename
