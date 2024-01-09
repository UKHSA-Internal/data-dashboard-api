from collections import OrderedDict

from caching.internal_api_client import InternalAPIClient


class GeographiesAPICrawler:
    """Crawls the `geographies/types` endpoints for all possible combinations"""

    def __init__(self, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client

    def process_geographies_api(self) -> dict[str, list[str]]:
        """Crawls the list and retrieve/detail endpoints associated with the geographies API

        Notes:
            This traverses the retrieve/detail endpoint for
            every available geography type

        Returns:
            Dict of geography type names keyed
            by a list of associated geography names.
            E.g.
            >>> {
                    "Nation": ["England", ...],
                    "Lower Tier Local Authority": ["Birmingham", ...]
                }

        """
        response = self._internal_api_client.hit_geographies_list_endpoint()
        return self.hit_detail_endpoint_for_each_geography_type(
            response_data=response.data
        )

    def hit_detail_endpoint_for_each_geography_type(
        self, response_data: list[OrderedDict]
    ) -> dict[str, list[str]]:
        """Traverses the retrieve/detail endpoint associated with each ID from the given `response_data`

        Returns:
            Dict of geography type names keyed
            by a list of associated geography names.
            E.g.
            >>> {
                    "Nation": ["England", ...],
                    "Lower Tier Local Authority": ["Birmingham", ...]
                }

        Raises:
            `KeyError`: If an object in the `response_data`
                does not contain an "id" key

        """
        data = {}
        for geography_type_data in response_data:
            geography_type_name: str = geography_type_data["name"]
            geography_type_id: int = geography_type_data["id"]

            geography_names: list[
                str
            ] = self.get_associated_geography_names_for_geography_type(
                geography_type_id=geography_type_id
            )
            data[geography_type_name] = geography_names

        return data

    def get_associated_geography_names_for_geography_type(
        self, geography_type_id: int
    ) -> list[str]:
        """Fetches the returned names associated with each geography from the detail endpoint`

        Returns:
            List of geography names associated with
            the given `geography_type_id`

        Raises:
            `KeyError`: If no geographies are returned

        """
        response = self._internal_api_client.hit_geographies_detail_endpoint(
            geography_type_id=geography_type_id
        )
        response_data = response.data
        return [
            geography_data["name"] for geography_data in response_data["geographies"]
        ]
