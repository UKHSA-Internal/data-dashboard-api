import pytest

from caching.private_api.crawler.cms_blocks import CMSBlockParser
from caching.private_api.crawler.geographies_crawler import GeographyData
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


class TestCMSBlocksRebuildChartBlockForGeography:
    @pytest.mark.parametrize(
        "geography_data",
        [
            GeographyData(
                name="Reading", geography_type_name="Lower Tier Local Authority"
            ),
            GeographyData(name="Wales", geography_type_name="Nation"),
        ],
    )
    def test_returns_correct_chart_block_with_injected_geography_information(
        self,
        geography_data: GeographyData,
        example_chart_block: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a chart block and an enriched `GeographyData` model
        When `rebuild_chart_block_for_geography()` is called
            from the `CMSBlockParser` class
        Then a copy of the chart block is returned
            with the geography data injected into the chart plots
        """
        # Given
        base_chart_block = example_chart_block

        # When
        rebuilt_chart_block = CMSBlockParser.rebuild_chart_block_for_geography(
            chart_block=base_chart_block, geography_data=geography_data
        )

        # Then
        assert (
            rebuilt_chart_block["chart"][0]["value"]["geography"] == geography_data.name
        )
        assert (
            rebuilt_chart_block["chart"][0]["value"]["geography_type"]
            == geography_data.geography_type_name
        )
