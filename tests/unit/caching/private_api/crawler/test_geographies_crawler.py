from unittest import mock

from caching.private_api.crawler.geographies_crawler import (
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
            geography_names=geography_names,
        )

        # When
        all_geography_combinations = (
            geography_type_data.export_all_geography_combinations()
        )

        # Then
        expected_geography_combinations = [
            GeographyData(name=x, geography_type_name=geography_type_name)
            for x in geography_names
        ]
        assert all_geography_combinations == expected_geography_combinations


class TestGeographiesAPICrawler:
    @mock.patch.object(
        GeographiesAPICrawler, "hit_detail_endpoint_for_each_geography_type"
    )
    def test_process_geographies_api(
        self, spy_hit_detail_endpoint_for_each_geography_type: mock.MagicMock
    ):
        """
        Given an instance of the `GeographiesAPICrawler`
        When the `process_geographies_api()` method is called
        Then the call is delegated to the `InternalAPIClient`
        And to the `hit_detail_endpoint_for_each_geography_type()` method
        """
        # Given
        spy_internal_api_client = mock.Mock()
        geographies_api_crawler = GeographiesAPICrawler(
            internal_api_client=spy_internal_api_client
        )

        # When
        geographies_api_crawler.process_geographies_api()

        # Then
        spy_internal_api_client.hit_geographies_list_endpoint.assert_called_once()
        returned_response = (
            spy_internal_api_client.hit_geographies_list_endpoint.return_value
        )

        spy_hit_detail_endpoint_for_each_geography_type.assert_called_once_with(
            response_data=returned_response.data
        )

    @mock.patch.object(
        GeographiesAPICrawler, "get_associated_geography_names_for_geography_type"
    )
    def test_hit_detail_endpoint_for_each_geography_type(
        self, spy_get_associated_geography_names_for_geography_type: mock.MagicMock
    ):
        """
        Given a dict containing geography_type IDs
        When `crawl_geographies_api()` is called
            from an instance of the `GeographiesAPICrawler`
        Then the call is delegated to the `InternalAPIClient` for each ID

        Patches:
            `spy_get_associated_geography_names_for_geography_type`: For
                the main assertion of checking each geography type ID
                is used for the detail endpoint call.
        """
        # Given
        fake_response_data = [
            {"id": 1, "name": "Nation"},
            {"id": 2, "name": "Lower Tier Local Authority"},
        ]
        spy_internal_api_client = mock.Mock()
        geographies_api_crawler = GeographiesAPICrawler(
            internal_api_client=spy_internal_api_client
        )

        # When
        geographies_api_crawler.hit_detail_endpoint_for_each_geography_type(
            response_data=fake_response_data
        )

        # Then
        fake_geography_type_ids = [x["id"] for x in fake_response_data]
        expected_calls = [
            mock.call(geography_type_id=fake_geography_type_id)
            for fake_geography_type_id in fake_geography_type_ids
        ]
        spy_get_associated_geography_names_for_geography_type.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch.object(
        GeographiesAPICrawler, "get_associated_geography_names_for_geography_type"
    )
    def test_hit_detail_endpoint_for_each_geography_type_returns_enriched_data_models(
        self, spy_get_associated_geography_names_for_geography_type: mock.MagicMock
    ):
        """
        Given a dict containing geography_type IDs
        And geography names returned from the call to
            `get_associated_geography_names_for_geography_type()`
        When `crawl_geographies_api()` is called
            from an instance of the `GeographiesAPICrawler`
        Then an enriched `GeographyTypeData` model is returned

        Patches:
            `spy_get_associated_geography_names_for_geography_type`: To
                remove the side effect of hitting the geographies API
                and injecting the returned geography names
        """
        # Given
        fake_response_data = [{"id": 1, "name": "Lower Tier Local Authority"}]
        fake_geography_names = ["Birmingham", "Crawley", "Liverpool"]
        spy_get_associated_geography_names_for_geography_type.return_value = (
            fake_geography_names
        )
        spy_internal_api_client = mock.Mock()
        geographies_api_crawler = GeographiesAPICrawler(
            internal_api_client=spy_internal_api_client
        )

        # When
        geography_data_models: list[
            GeographyTypeData
        ] = geographies_api_crawler.hit_detail_endpoint_for_each_geography_type(
            response_data=fake_response_data
        )

        # Then
        geography_data_model = geography_data_models[0]
        assert geography_data_model.name == fake_response_data[0]["name"]
        assert geography_data_model.geography_names == fake_geography_names

    def test_logs_are_recorded_for_completion_of_geographies_api(
        self, caplog: LogCaptureFixture
    ):
        """
        Given a mocked response containing georgraphy names
        When `get_associated_geography_names_for_geography_type()` is called
            from an instance of the `GeographiesAPICrawler`
        Then the expected geography names are returned
        """
        # Given
        expected_response = {
            "geographies": [
                {"id": 2, "name": "Birmingham"},
                {"id": 3, "name": "Barrow-in-Furness"},
                {"id": 4, "name": "Worthing"},
            ]
        }
        spy_internal_api_client = mock.Mock()
        mocked_response = mock.Mock(data=expected_response)
        spy_internal_api_client.hit_geographies_detail_endpoint.return_value = (
            mocked_response
        )

        geographies_api_crawler = GeographiesAPICrawler(
            internal_api_client=spy_internal_api_client
        )

        # When
        associated_geography_names = (
            geographies_api_crawler.get_associated_geography_names_for_geography_type(
                geography_type_id=mock.Mock()
            )
        )

        # Then
        expected_geography_names: list[str] = [
            x["name"] for x in expected_response["geographies"]
        ]
        assert associated_geography_names == expected_geography_names
