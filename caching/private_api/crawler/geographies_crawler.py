from collections import OrderedDict
from dataclasses import dataclass

from caching.internal_api_client import InternalAPIClient


@dataclass
class GeographyData:
    name: str
    geography_type_name: str

    def __eq__(self, other: "GeographyData") -> bool:
        return (
            self.name == other.name
            and self.geography_type_name == other.geography_type_name
        )


@dataclass
class GeographyTypeData:
    name: str
    geography_names: list[str]


class GeographiesAPICrawler:
    """Crawls the `geographies/types` endpoints for all possible combinations"""

    def __init__(self, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client

    def process_geographies_api(self) -> list[GeographyTypeData]:
        """Crawls the list and retrieve/detail endpoints associated with the geographies API

        Notes:
            This traverses the retrieve/detail endpoint for
            every available geography type

        Returns:
            List of enriched `GeographyTypeData` models
            which hold the geography type name
            and its associated geography names
            E.g.
            >>> [
                    GeographyData(name="Nation", geography_names=["England", ...]),
                    GeographyData(name="Lower Tier Local Authority", geography_names=["Birmingham", ...]),
                ]

        """
        response = self._internal_api_client.hit_geographies_list_endpoint()
        return self.hit_detail_endpoint_for_each_geography_type(
            response_data=response.data
        )

    def hit_detail_endpoint_for_each_geography_type(
        self, response_data: list[OrderedDict]
    ) -> list[GeographyTypeData]:
        """Traverses the retrieve/detail endpoint associated with each ID from the given `response_data`

        Returns:
            List of enriched `GeographyTypeData` models
            which hold the geography type name
            and its associated geography names
            E.g.
            >>> [
                    GeographyData(name="Nation", geography_names=["England", ...]),
                    GeographyData(name="Lower Tier Local Authority", geography_names=["Birmingham", ...]),
                ]

        Raises:
            `KeyError`: If an object in the `response_data`
                does not contain an "id" key

        """
        data = []
        for geography_type_data in response_data:
            geography_names: list[
                str
            ] = self.get_associated_geography_names_for_geography_type(
                geography_type_id=geography_type_data["id"]
            )

            geography_type_data = GeographyTypeData(
                name=geography_type_data["name"], geography_names=geography_names
            )
            data.append(geography_type_data)

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
