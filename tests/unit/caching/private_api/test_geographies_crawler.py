from unittest import mock

from caching.private_api.geographies_crawler import GeographiesAPICrawler


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

    def test_hit_detail_endpoint_for_each_geography_type(self):
        """
        Given a dict containing geography_type IDs
        When `crawl_geographies_api()` is called
            from an instance of the `GeographiesAPICrawler`
        Then the call is delegated to the `InternalAPIClient` for each ID
        """
        # Given
        fake_geography_type_ids = [1, 2, 3]
        fake_response_data = [
            {"id": fake_geography_type_id}
            for fake_geography_type_id in fake_geography_type_ids
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
        expected_calls = [
            mock.call(geography_type_id=fake_geography_type_id)
            for fake_geography_type_id in fake_geography_type_ids
        ]
        spy_internal_api_client.hit_geographies_detail_endpoint.assert_has_calls(
            calls=expected_calls, any_order=True
        )
