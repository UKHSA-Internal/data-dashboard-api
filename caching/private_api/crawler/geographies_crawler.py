import logging
from dataclasses import dataclass

from rest_framework.response import Response

from caching.internal_api_client import InternalAPIClient

logger = logging.getLogger(__name__)


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

    def export_all_geography_combinations(self) -> list[GeographyData]:
        return [
            GeographyData(name=geography_name, geography_type_name=self.name)
            for geography_name in self.geography_names
        ]


class GeographiesAPICrawler:
    """Crawls the `geographies/types` endpoints for all possible combinations"""

    def __init__(self, internal_api_client: InternalAPIClient):
        self._internal_api_client = internal_api_client

    def hit_list_endpoint_for_topic(self, topic: str) -> list[GeographyTypeData]:
        """Hits the endpoint for the given `topic` to fetch the associated available geographies

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
            `KeyError`: If the response schema is not
                in the expected structure

        """
        response: Response = self._internal_api_client.hit_geographies_list_endpoint(
            topic=topic
        )
        geography_type_data_models: list[GeographyTypeData] = (
            self._convert_to_geography_type_models(response_data=response.data)
        )

        logger.info("Completed processing of geographies API for `%s` page", topic)
        return geography_type_data_models

    @staticmethod
    def _convert_to_geography_type_models(
        response_data: dict,
    ) -> list[GeographyTypeData]:
        geography_type_data_models = []

        for geography_type_data in response_data:
            geography_type_name: str = geography_type_data["geography_type"]
            geographies: list[dict[str, str]] = geography_type_data["geographies"]

            geography_type = GeographyTypeData(
                name=geography_type_name,
                geography_names=[geography["name"] for geography in geographies],
            )

            geography_type_data_models.append(geography_type)
        return geography_type_data_models
