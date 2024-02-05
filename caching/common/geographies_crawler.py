import logging
from dataclasses import dataclass

from rest_framework.response import Response

from caching.internal_api_client import InternalAPIClient
from cms.topic.models import TopicPage

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

    @property
    def url_friendly_name(self) -> str:
        return _convert_to_url_friendly_name(self.name)

    @property
    def url_friendly_geography_type_name(self) -> str:
        return _convert_to_url_friendly_name(self.geography_type_name)


def _convert_to_url_friendly_name(name: str) -> str:
    return name.replace(" ", "+")


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

    def __init__(self, internal_api_client: InternalAPIClient | None = None):
        self._internal_api_client = internal_api_client or InternalAPIClient()

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

    def get_geography_combinations_for_page(
        self, page: TopicPage
    ) -> list[GeographyData]:
        """Returns all available geographies for the given `topic` as enriched `GeographyData` models

        Args:
            page: The page model for which to retrieve
                geographies which are relevant for
                the selected topics on that page

        Returns:
            List of `GeographyData` containing the name
            and corresponding geography type name for each geography
            which are valid for the given `page`

        """
        selected_topic: str = page.selected_topics.pop()
        geography_type_data_models: list[GeographyTypeData] = (
            self.hit_list_endpoint_for_topic(topic=selected_topic)
        )

        return [
            geography_data
            for geography_type_data in geography_type_data_models
            for geography_data in geography_type_data.export_all_geography_combinations()
        ]
