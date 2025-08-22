import pytest

from cms.dynamic_content.global_filter_deconstruction import GlobalFilterCMSBlockParser


class TestGlobalFilterCMSBlockParser:
    @pytest.mark.parametrize(
        "index, date_from, date_to, topic",
        [
            (0, "2023-04-01", "2024-03-31", "6-in-1"),
            (1, "2024-04-01", "2025-03-31", "6-in-1"),
            (2, "2023-04-01", "2024-03-31", "MMR1"),
            (3, "2024-04-01", "2025-03-31", "MMR1"),
        ],
    )
    def test_build_complete_payloads_for_maps_api(
        self,
        index: int,
        date_from: str,
        date_to: str,
        topic: str,
        example_global_filter: str,
    ):
        """
        Given an example global filter CMS block
        When `build_complete_payloads_for_maps_api()` is called
            from an instance of the `GlobalFilterCMSBlockParser`
        Then the dictionaries returned represent
            each time period / data filter combination
        """
        # Given
        global_filter = example_global_filter
        global_filter_block_parser = GlobalFilterCMSBlockParser(
            global_filter=global_filter
        )

        # When
        complete_payloads_for_maps_api = (
            global_filter_block_parser.build_complete_payloads_for_maps_api()
        )

        # Then
        individual_payload = complete_payloads_for_maps_api[index]
        expected_parameters = {
            "age": "all",
            "geographies": [],
            "geography_type": "Upper Tier Local Authority",
            "metric": f"{topic}_coverage_coverageByYear",
            "sex": "all",
            "stratum": "12m",
            "sub_theme": "childhood-vaccines",
            "theme": "immunisation",
            "topic": topic,
        }
        accompanying_points = individual_payload["accompanying_points"]

        expected_payload = {
            "date_from": date_from,
            "date_to": date_to,
            "accompanying_points": accompanying_points,
            "parameters": expected_parameters,
        }

        assert individual_payload == expected_payload
