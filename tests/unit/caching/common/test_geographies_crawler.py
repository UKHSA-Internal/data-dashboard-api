from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.common.geographies_crawler import (
    GeographiesAPICrawler,
    GeographyData,
    GeographyTypeData,
)


class TestGeographyTypeData:
    def test_export_all_geography_combinations(self):
        """
        Given an enriched `GeographyTypeData` model
        When `export_all_geography_combinations()` is called
            from the `GeographyTypeData` model
        Then the correct `GeographyData` models are returned
        """
        # Given
        geography_type_name = "Nation"
        geography_names = ["England", "Wales"]
        geography_type_data = GeographyTypeData(
            name=geography_type_name,
            geographies=geography_names,
        )

        # When
        all_geography_combinations = (
            geography_type_data.export_all_geography_combinations()
        )

        # Then
        expected_geography_combinations = [
            GeographyData(name=x, geography_type=geography_type_name)
            for x in geography_names
        ]
        assert all_geography_combinations == expected_geography_combinations


class TestGeographiesAPICrawler:
    def test_hit_list_endpoint_for_topic_returns_enriched_data_models(self):
        """
        Given a topic
        And geography names returned from the call to
            `hit_geographies_list_endpoint()` on the `InternalAPIClient`
        When `hit_list_endpoint_for_topic()` is called
            from an instance of the `GeographiesAPICrawler`
        Then a list of enriched `GeographyTypeData` model are returned
        """
        # Given
        topic = "COVID-19"
        fake_geography_names = ["Birmingham", "Crawley", "Liverpool"]
        fake_response_data = [
            {
                "geography_type": "Lower Tier Local Authority",
                "geographies": [{"name": x} for x in fake_geography_names],
            }
        ]
        fake_response = mock.Mock(data=fake_response_data)

        spy_internal_api_client = mock.Mock()
        spy_internal_api_client.hit_geographies_list_endpoint.return_value = (
            fake_response
        )
        geographies_api_crawler = GeographiesAPICrawler(
            internal_api_client=spy_internal_api_client
        )

        # When
        geography_type_data_models: list[GeographyTypeData] = (
            geographies_api_crawler.hit_list_endpoint_for_topic(topic=topic)
        )

        # Then
        geography_type_data_model = geography_type_data_models[0]
        assert geography_type_data_model.name == fake_response_data[0]["geography_type"]
        assert geography_type_data_model.geographies == fake_geography_names

    def test_logs_are_recorded_for_completion_of_geographies_api(
        self, caplog: LogCaptureFixture
    ):
        """
        Given a topic
        When `hit_list_endpoint_for_topic()` is called
            from an instance of `GeographiesAPICrawler`
        Then the correct logs are made for
            the processing of the geographies API
        """
        # Given
        topic = "COVID-19"
        mocked_internal_api_client = mock.Mock()
        mocked_internal_api_client.hit_geographies_list_endpoint = mock.MagicMock
        geographies_api_crawler = GeographiesAPICrawler(
            internal_api_client=mocked_internal_api_client
        )

        # When
        geographies_api_crawler.hit_list_endpoint_for_topic(topic=topic)

        # Then
        expected_log = f"Completed processing of geographies API for `{topic}` page"
        assert expected_log in caplog.text

    @mock.patch.object(GeographiesAPICrawler, "hit_list_endpoint_for_topic")
    def test_get_geography_combinations_for_page(
        self, spy_hit_list_endpoint_for_topic: mock.MagicMock
    ):
        """
        Given a topic and mocked return `GeographyTypeData` models
        When `get_geography_combinations_for_page()` is called
            from an instance of the `GeographiesAPICrawler`
        Then the correct list of `GeographyData` models are returned

        Patches:
            `spy_hit_list_endpoint_for_topic`: To remove the side effect
                of hitting the geographies API and making db queries

        """
        # Given
        ltha = "Lower Tier Local Authority"
        geography_type_data_models = [
            GeographyTypeData(
                name=ltha, geographies=["Bexley", "Hackney", "Tower Hamlets"]
            )
        ]
        spy_hit_list_endpoint_for_topic.return_value = geography_type_data_models

        topic = "COVID-19"
        mocked_page = mock.Mock(selected_topics={topic})
        geographies_api_crawler = GeographiesAPICrawler()

        # When
        geography_combinations: list[GeographyData] = (
            geographies_api_crawler.get_geography_combinations_for_page(
                page=mocked_page
            )
        )

        # Then
        # Check the `GeographiesAPICrawler` is used correctly to
        # fetch the correct geographies for the given topic
        spy_hit_list_endpoint_for_topic.assert_called_once_with(topic=topic)

        # Check the returned `GeographyData` models are correct
        assert len(geography_combinations) == 3
        assert geography_combinations[0].geography_type
        assert geography_combinations[0].name == "Bexley"

        assert geography_combinations[1].geography_type
        assert geography_combinations[1].name == "Hackney"

        assert geography_combinations[2].geography_type
        assert geography_combinations[2].name == "Tower Hamlets"
