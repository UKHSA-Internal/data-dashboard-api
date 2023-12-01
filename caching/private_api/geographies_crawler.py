from collections import OrderedDict

from caching.internal_api_client import InternalAPIClient


class GeographiesAPICrawler:
    """Crawls the `geographies/types` endpoints for all possible combinations"""

    def __init__(self, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client

    def process_geographies_api(self) -> None:
        """Crawls the list and retrieve/detail endpoints associated with the geographies API

        Notes:
            This traverses the retrieve/detail endpoint for
            every available geography type

        Returns:
            None

        """
        response = self._internal_api_client.hit_geographies_list_endpoint()
        self.hit_detail_endpoint_for_each_geography_type(response_data=response.data)

    def hit_detail_endpoint_for_each_geography_type(
        self, response_data: list[OrderedDict]
    ) -> None:
        """Traverses the retrieve/detail endpoint associated with each ID from the given `response_data`

        Returns:
            None

        Raises:
            `KeyError`: If an object in the `response_data`
                does not contain an "id" key

        """
        for geography_type_data in response_data:
            geography_type_id = geography_type_data["id"]
            self._internal_api_client.hit_geographies_detail_endpoint(
                geography_type_id=geography_type_id
            )
