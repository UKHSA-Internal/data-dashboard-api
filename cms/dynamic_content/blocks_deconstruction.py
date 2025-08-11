import copy

CMS_COMPONENT_BLOCK_TYPE = dict[str, str | dict[str, str] | list[dict[str, str]]]


class CMSBlockParser:
    """This is used to deconstruct CMS blocks into pieces which can then be handled by the `RequestPayloadBuilder`

    Notes:
        Generally the hierarchy of CMS component blocks is as follows:

            content cards -> row cards -> cards -> blocks

        Whereby the content cards are the uppermost level.
        And blocks containing the data which can then be
        passed to the `RequestPayloadBuilder` and then
        subsequently requests can then be made against
        the corresponding endpoint via
        the `DynamicContentBlockCrawler`.

    """

    # Extraction of charts

    @classmethod
    def get_all_chart_blocks_from_section_for_geography(
        cls, *, section: CMS_COMPONENT_BLOCK_TYPE, geography_data
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Extracts a list of all chart cards from the given `section` for the specific `geography_data`

        Args:
            section: The section component from the CMS
            geography_data: An optional enriched `GeographyData` model,
                containing the name of the geography
                and its parent geography type.
                If not provided, then the base choices from
                the CMS blocks will be used

        Returns:
            A list of chart card dictionaries

        """
        all_chart_blocks_from_section: list[CMS_COMPONENT_BLOCK_TYPE] = (
            cls.get_all_chart_blocks_from_section(section=section)
        )
        if not geography_data:
            return all_chart_blocks_from_section

        return [
            cls.rebuild_chart_block_for_geography(
                chart_block=chart_block, geography_data=geography_data
            )
            for chart_block in all_chart_blocks_from_section
        ]

    @classmethod
    def get_chart_blocks_from_chart_row_cards(
        cls, *, chart_row_cards: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Extracts all chart blocks from the given list of `chart_row_cards`

        Args:
            chart_row_cards: List of all chart row cards on the page

        Returns:
            List of chart blocks which can then be crawled accordingly
            Note that these blocks may still also contain headline
            blocks within them.

        """
        try:
            return [
                chart_card["value"]
                for chart_row_card in chart_row_cards
                for chart_card in chart_row_card["value"]["columns"]
            ]
        except KeyError:
            return []

    @classmethod
    def get_all_chart_blocks_from_section(
        cls, *, section: CMS_COMPONENT_BLOCK_TYPE
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Extracts a list of all chart cards from the given `section`

        Args:
            section: The section component from the CMS

        Returns:
            A list of chart block dictionaries

        """
        chart_row_cards = cls.get_chart_row_cards_from_page_section(section=section)
        return cls.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=chart_row_cards
        )

    @classmethod
    def rebuild_chart_block_for_geography(
        cls, *, chart_block: CMS_COMPONENT_BLOCK_TYPE, geography_data: "GeographyData"
    ) -> CMS_COMPONENT_BLOCK_TYPE:
        """Builds a copy of the given `chart_block` with the `geography_data` applied

        Args:
            chart_block:
                A single chart block which could be crawled accordingly.
                Note that this blocks may still also contain headline
                blocks within it.
            geography_data:
                An enriched `GeographyData` model,
                containing the name of the geography
                and its parent geography type.

        Returns:
            The single chart block with the `geograpy_data`
            injected into the geography fields on each
            plot of the chart block.

        """
        chart_block_with_geography = copy.deepcopy(chart_block)
        for plot in chart_block_with_geography["chart"]:
            plot["value"]["geography_type"] = geography_data.geography_type
            plot["value"]["geography"] = geography_data.name

        return chart_block_with_geography

    # Extraction of headline number blocks

    @classmethod
    def get_all_headline_blocks_from_section(
        cls, *, section: CMS_COMPONENT_BLOCK_TYPE
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Extracts a list of all headline number blocks from the given `section`

        Args:
            section: The section component from the CMS

        Returns:
            A list of headline number block dictionaries

        """
        content_cards = cls.get_content_cards_from_section(section=section)
        headline_numbers_row_cards = (
            cls.get_headline_numbers_row_cards_from_content_cards(
                content_cards=content_cards
            )
        )
        headline_blocks = cls.get_headline_blocks_from_headline_number_row_cards(
            headline_numbers_row_cards=headline_numbers_row_cards
        )

        # Headline blocks can also be places within chart cards.
        # So they have to be extracted from any charts cards in the section
        chart_row_cards = cls.get_chart_row_cards_from_content_cards(
            content_cards=content_cards
        )
        chart_blocks = cls.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=chart_row_cards
        )
        headline_blocks += cls.get_headline_blocks_from_chart_blocks(
            chart_blocks=chart_blocks
        )
        return headline_blocks

    @classmethod
    def get_content_cards_from_section(
        cls,
        *,
        section: dict[list[CMS_COMPONENT_BLOCK_TYPE]],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of content cards from the given `section`

        Args:
            section: The section dict from the CMS

        Returns:
            A list of content card dicts

        """
        return section["value"]["content"]

    @classmethod
    def get_chart_row_cards_from_content_cards(
        cls,
        *,
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of chart row from the given `content_cards`

        Args:
            content_cards: The list of content card dicts
                from the CMS

        Returns:
            A list of chart row card dicts which can be processed

        """
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "chart_row_card"
        ]

    @classmethod
    def get_chart_row_cards_from_page_section(
        cls,
        *,
        section: dict[list[CMS_COMPONENT_BLOCK_TYPE]],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Get chart row cards from page section.

        Args:
            section: a page section to be processed for chart card data

        Returns:
            A list of dictionaries containing chart row cards from page section,
        """
        content_cards = cls.get_content_cards_from_section(section=section)
        return cls.get_chart_row_cards_from_content_cards(content_cards=content_cards)

    @classmethod
    def get_headline_blocks_from_chart_blocks(
        cls, *, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Extracts all headline number blocks from the given list of `chart_blocks`

        Args:
            chart_blocks: List of all chart blocks on the page

        Returns:
            List of headline number blocks which can then be crawled accordingly

        """
        headline_number_blocks = []

        for chart_block in chart_blocks:
            headline_number_blocks_in_chart_block = chart_block.get(
                "headline_number_columns", []
            )
            headline_number_blocks += headline_number_blocks_in_chart_block

        return headline_number_blocks

    @classmethod
    def get_headline_numbers_row_cards_from_content_cards(
        cls,
        *,
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of headliner number row cards from the given `content_cards`

        Args:
            content_cards: The list of content card dicts
                from the CMS

        Returns:
            A list of headline number row card dicts
            which can be processed

        """
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "headline_numbers_row_card"
        ]

    @classmethod
    def get_headline_blocks_from_headline_number_row_cards(
        cls,
        *,
        headline_numbers_row_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Extracts all headline number blocks from the given list of `headline_numbers_row_cards`

        Args:
            headline_numbers_row_cards: List of all headline number row cards
                on the page

        Returns:
            List of headline number blocks which can then be crawled accordingly

        """
        try:
            return [
                block
                for headline_numbers_row_card in headline_numbers_row_cards
                for column in headline_numbers_row_card["value"]["columns"]
                for block in column["value"]["rows"]
            ]
        except KeyError:
            return []

    @classmethod
    def get_global_filter_cards_from_content_cards(
        cls,
        *,
        content_cards: list[CMS_COMPONENT_BLOCK_TYPE],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Filters for a list of global filters from the given `content_cards`

        Args:
            content_cards: The list of content card dicts
                from the CMS

        Returns:
            A list of global filter row dicts which can be processed

        """
        return [
            content_card
            for content_card in content_cards
            if content_card["type"] == "global_filter_card"
        ]

    @classmethod
    def get_global_filter_cards_from_page_section(
        cls,
        *,
        section: dict[list[CMS_COMPONENT_BLOCK_TYPE]],
    ) -> list[CMS_COMPONENT_BLOCK_TYPE]:
        """Get all global filter cards from page section.

        Args:
            section: a page section to be processed for chart card data

        Returns:
            A list of dictionaries containing global filter cards from page section,
        """
        content_cards = cls.get_content_cards_from_section(section=section)
        return cls.get_global_filter_cards_from_content_cards(
            content_cards=content_cards
        )

    # Extraction of selected topics

    @classmethod
    def get_all_selected_topics_from_sections(cls, *, sections) -> set[str]:
        """Extracts a set of topics from all headline & chart blocks in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the list of given `sections`

        """
        selected_topics_from_headline_blocks: set[str] = (
            cls._get_all_selected_topics_in_headline_blocks_from_sections(
                sections=sections
            )
        )
        selected_topics_from_chart_blocks: set[str] = (
            cls._get_all_selected_topics_in_chart_blocks_from_sections(
                sections=sections
            )
        )
        return selected_topics_from_chart_blocks.union(
            selected_topics_from_headline_blocks,
        )

    @classmethod
    def _get_all_selected_topics_in_chart_blocks_from_sections(
        cls, *, sections: list[dict[list[CMS_COMPONENT_BLOCK_TYPE]]]
    ) -> set[str]:
        """Extracts a set of topics from all chart blocks in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the list of given `sections`

        """
        chart_blocks = []
        for section in sections:
            chart_blocks += cls.get_all_chart_blocks_from_section(section=section)

        return cls.get_all_selected_topics_from_chart_blocks(chart_blocks=chart_blocks)

    @classmethod
    def _get_all_selected_topics_in_headline_blocks_from_sections(
        cls, *, sections: list[dict[list[CMS_COMPONENT_BLOCK_TYPE]]]
    ) -> set[str]:
        """Extracts a set of topics from all headline blocks in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the list of given `sections`

        """
        headline_blocks = []
        for section in sections:
            headline_blocks += cls.get_all_headline_blocks_from_section(section=section)

        return cls.get_all_selected_topics_from_headline_blocks(
            headline_blocks=headline_blocks
        )

    @classmethod
    def get_all_selected_topics_from_chart_blocks(
        cls, *, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> set[str]:
        """Extracts a set of topics from the given `chart_blocks`

        Args:
            chart_blocks: List of chart blocks
                from which to extract the unique
                selected topics

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the list of given `chart_blocks`

        """
        return {
            plot["value"]["topic"] for block in chart_blocks for plot in block["chart"]
        }

    @classmethod
    def get_all_selected_topics_from_headline_blocks(
        cls, *, headline_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> set[str]:
        """Extracts a set of topics from the given `headline_blocks`

        Args:
            headline_blocks: List of headline number blocks
                from which to extract the unique
                selected topics

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the list of given `headline_blocks`

        """
        return {block["value"]["topic"] for block in headline_blocks}

    # Extraction of selected topics

    @classmethod
    def get_all_selected_metrics_from_sections(cls, *, sections) -> set[str]:
        """Extracts a set of metrics from all headline & chart blocks in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a metric which has been selected at least
            once in the list of given `sections`

        """
        selected_metrics_from_headline_blocks: set[str] = (
            cls._get_all_selected_metrics_in_headline_blocks_from_sections(
                sections=sections
            )
        )
        selected_metrics_from_chart_blocks: set[str] = (
            cls._get_all_selected_metrics_in_chart_blocks_from_sections(
                sections=sections
            )
        )
        selected_metrics_from_global_filters: set[str] = (
            cls._get_all_selected_metrics_in_global_filters_from_sections(
                sections=sections
            )
        )
        return selected_metrics_from_chart_blocks.union(
            selected_metrics_from_headline_blocks,
            selected_metrics_from_global_filters,
        )

    @classmethod
    def _get_all_selected_metrics_in_chart_blocks_from_sections(
        cls, *, sections: list[dict[list[CMS_COMPONENT_BLOCK_TYPE]]]
    ) -> set[str]:
        """Extracts a set of metrics from all chart blocks in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a metric which has been selected at least
            once in the list of given `sections`

        """
        chart_blocks = []
        for section in sections:
            chart_blocks += cls.get_all_chart_blocks_from_section(section=section)

        return cls.get_all_selected_metrics_from_chart_blocks(chart_blocks=chart_blocks)

    @classmethod
    def _get_all_selected_metrics_in_headline_blocks_from_sections(
        cls, *, sections: list[dict[list[CMS_COMPONENT_BLOCK_TYPE]]]
    ) -> set[str]:
        """Extracts a set of metrics from all headline blocks in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a metric which has been selected at least
            once in the list of given `sections`

        """
        headline_blocks = []
        for section in sections:
            headline_blocks += cls.get_all_headline_blocks_from_section(section=section)

        return cls.get_all_selected_metrics_from_headline_blocks(
            headline_blocks=headline_blocks
        )

    @classmethod
    def get_all_selected_metrics_from_chart_blocks(
        cls, *, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> set[str]:
        """Extracts a set of metrics from the given `chart_blocks`

        Args:
            chart_blocks: List of chart blocks
                from which to extract the unique
                selected metrics

        Returns:
            Set of strings where each string represents
            a metric which has been selected at least
            once in the list of given `chart_blocks`

        """
        return {
            plot["value"]["metric"] for block in chart_blocks for plot in block["chart"]
        }

    @classmethod
    def get_all_selected_metrics_from_headline_blocks(
        cls, *, headline_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> set[str]:
        """Extracts a set of metrics from the given `headline_blocks`

        Args:
            headline_blocks: List of headline number blocks
                from which to extract the unique
                selected metrics

        Returns:
            Set of strings where each string represents
            a metric which has been selected at least
            once in the list of given `headline_blocks`

        """
        return {block["value"]["metric"] for block in headline_blocks}

    @classmethod
    def _get_all_selected_metrics_in_global_filters_from_sections(
        cls, *, sections: list[dict[list[CMS_COMPONENT_BLOCK_TYPE]]]
    ) -> set[str]:
        """Extracts a set of topics from all global filters in the given `sections`

        Args:
            sections: List of all CMS section components
                from the target page

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the list of given `sections`

        """
        global_filters = cls._get_all_global_filter_cards_in_sections(sections=sections)
        return cls.get_all_selected_metrics_from_global_filters(
            global_filters=global_filters
        )

    @classmethod
    def _get_all_global_filter_cards_in_sections(cls, sections: list) -> list[dict]:
        global_filters = []
        for section in sections:
            global_filters += cls.get_global_filter_cards_from_page_section(
                section=section
            )
        return global_filters

    @classmethod
    def get_all_selected_metrics_from_global_filters(
        cls, *, global_filters: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> set[str]:
        """Extracts a set of metrics from the given `chart_blocks`

        Args:
            global_filters: List of global filter blocks
                from which to extract the unique
                selected metrics

        Returns:
            Set of strings where each string represents
            a metrics which has been selected at least
            once in the list of given `global_filters`

        """
        selected_topics: set[str] = set()
        for global_filter in global_filters:
            data_filters = cls._extract_data_filters_from_global_filters(
                global_filter=global_filter
            )
            for data_filter in data_filters:
                individual_filter = data_filter["value"]
                selected_topics.add(individual_filter["parameters"]["metric"]["value"])

        return selected_topics

    @classmethod
    def _extract_data_filters_from_global_filters(cls, *, global_filter):
        data_filters = []
        for row in global_filter["value"]["rows"]:
            for filter_block in row["value"]["filters"]:
                if filter_block["type"] == "data_filters":
                    data_filters.extend(filter_block["value"]["data_filters"])
        return data_filters
