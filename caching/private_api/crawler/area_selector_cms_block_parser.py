import copy

from caching.private_api.crawler.geographies_crawler import (
    GeographiesAPICrawler,
    GeographyTypeData,
)
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


class AreaSelectorCMSBlockParser:
    """Used to produce all possible geography combinations for chart/headline blocks"""
    def __init__(
        self,
        geographies_api_crawler: GeographiesAPICrawler,
    ):
        self._geographies_api_crawler = geographies_api_crawler
        self._geography_type_data_combinations: list[
            GeographyTypeData
        ] = self._geographies_api_crawler.process_geographies_api()

    def build_all_possible_headline_block_combinations(
        self, headline_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Builds all possible geography permutations for the given `headline_block`

        Args:
            headline_block: The base headline block
                to create the geography-related permutations for

        Returns:
            List of content blocks, each with an
            individual geography combination.
            E.g.
            >>> [
                    {"value": {"topic": "COVID-19",
                               "geography": "England",
                               "geography_type": "Nation", ...
                               }, ...
                     },
                    {"value": {"topic": "COVID-19",
                               "geography": "Birmingham",
                               "geography_type": "Lower Tier Local Authority", ...
                               }, ...
                     },
                     ...
                ]

        """
        content_block_combinations: list[CMS_COMPONENT_BLOCK_TYPE] = []

        for geography_type_data in self._geography_type_data_combinations:
            for geography_name in geography_type_data.geography_names:
                component_content_combo = copy.deepcopy(headline_block)
                component_content_combo["value"][
                    "geography_type"
                ] = geography_type_data.name
                component_content_combo["value"]["geography"] = geography_name

                content_block_combinations.append(component_content_combo)

        return content_block_combinations

    def build_all_possible_chart_block_combinations(
        self, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Builds all possible geography permutations for the given `chart_block`

        Args:
            chart_block: The base chart block
                to create the geography-related permutations for

        Returns:
            List of content blocks, each with an
            individual geography combination.
            E.g.
            >>> [
                    {"value": {"topic": "COVID-19",
                               "geography": "England",
                               "geography_type": "Nation", ...
                               }, ...
                     },
                    {"value": {"topic": "COVID-19",
                               "geography": "Birmingham",
                               "geography_type": "Lower Tier Local Authority", ...
                               }, ...
                     },
                     ...
                ]

        """
        chart_block_combinations: list[CMS_COMPONENT_BLOCK_TYPE] = []

        for geography_type_data in self._geography_type_data_combinations:
            for geography_name in geography_type_data.geography_names:
                component_content_combo = copy.deepcopy(chart_block)
                for plot in component_content_combo["chart"]:
                    plot["value"]["geography_type"] = geography_type_data.name
                    plot["value"]["geography"] = geography_name

                chart_block_combinations.append(component_content_combo)

        return chart_block_combinations
