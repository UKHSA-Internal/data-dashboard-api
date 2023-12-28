import pytest

from caching.private_api.crawler import PrivateAPICrawler


class TestCreateFileAndDirectoryNamesForChartCards:
    @pytest.mark.parametrize(
        "chart_card_names, formatted_chart_card_names",
        [
            (
                "chart card name with (20+) chars! - 10,000",
                "chart_card_name_with_20_chars_10000",
            ),
            (
                "another chart card title, covid cases (20,000+) / tests",
                "another_chart_card_title_covid_cases_20000_tests",
            ),
            (
                "charts - cards - cases & 54+ (7day)",
                "charts_cards_cases_54_7day",
            ),
            (
                r"charts,with\slashes/in-the-title-and-no-spaces",
                "chartswithslashesinthetitleandnospaces",
            ),
            (
                "Test top^&&*ic folder+ / CDD-1467 !@'()%",
                "test_topic_folder_cdd1467",
            ),
            (
                "t;:!est chart name@",
                "test_chart_name",
            ),
            (
                'test cdd-1467 spec.!"£$%^&**()?|:;/ial Characters',
                "test_cdd1467_special_characters",
            ),
        ],
    )
    def test_format_titles_for_filenames_behaves_correctly(
        self,
        chart_card_names: str,
        formatted_chart_card_names: str,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a string that contains special characters.
        When the `format_titles_for_filenames()` method is called.
        Then the string is formatted to remove special characters including spaces.
        """
        # Given
        fake_name = chart_card_names

        # When
        expected_filename = private_api_crawler_with_mocked_internal_api_client.format_titles_for_filenames(
            file_name=fake_name
        )

        # Then
        assert expected_filename == formatted_chart_card_names

    @pytest.mark.parametrize(
        "directory_names, formatted_directory_names",
        [
            (
                "directory name with spaces and (12+) / other characters!+",
                "directory_name_with_spaces_and_12_other_characters",
            ),
            (
                "directory with /slashes and-no-spaces",
                "directory_with_slashes_andnospaces",
            ),
            (
                "top$ic folder",
                "topic_folder",
            ),
            (
                r"t%:;£est\ 1467 /charts ()$%^* TEST?[]",
                "test_1467_charts_test",
            ),
        ],
    )
    def test_create_directory_name_for_downloads_behaves_correctly(
        self,
        directory_names: str,
        formatted_directory_names: str,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a fake directory name that contains special characters.
        When the `create_directory_for_downloads()` is called.
        Then the string is formatted to remove special characters.
        """
        # Given
        fake_directory_name = directory_names

        # When
        expected_file_name = private_api_crawler_with_mocked_internal_api_client.create_directory_name_for_downloads(
            file_name=fake_directory_name,
        )

        # Then
        assert expected_file_name == formatted_directory_names

    def test_data_dashboard_is_renamed_landing_page(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a directory name of "UKHSA data dashboard"
        When the `create_directory_name_for_downloads()` method id called.
        Then the directory name is changed to landing_page.
        """
        # Given
        fake_directory_name = "UKHSA data dashboard"

        # When
        expected_file_name = private_api_crawler_with_mocked_internal_api_client.create_directory_name_for_downloads(
            file_name=fake_directory_name,
        )

        # Then
        assert expected_file_name == "landing_page"

    def test_create_filename_for_chart_card_adds_file_extension(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a fake filename that contains special characters.
        When the `create_filename_for_chart_card()` is called.
        Then the string is formatted to remove special characters and suffixed
            with the appropriate file extension.
        """
        # Given
        fake_file_name = "chart card title"
        fake_file_format = "csv"

        # When
        expected_file_name = private_api_crawler_with_mocked_internal_api_client.create_filename_for_chart_card(
            file_name=fake_file_name,
            file_format=fake_file_format,
        )

        # Then
        assert expected_file_name == f"chart_card_title.{fake_file_format}"
