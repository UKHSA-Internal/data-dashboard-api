from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


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

    @classmethod
    def get_all_chart_blocks_from_section(
        cls, section: CMS_COMPONENT_BLOCK_TYPE
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
    def get_all_headline_blocks_from_section(
        cls, section: CMS_COMPONENT_BLOCK_TYPE
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
    def get_headline_numbers_row_cards_from_content_cards(
        cls,
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
    def get_chart_row_cards_from_page_section(
        cls,
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
    def get_headline_blocks_from_headline_number_row_cards(
        cls,
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
    def get_chart_blocks_from_chart_row_cards(
        cls, chart_row_cards: list[CMS_COMPONENT_BLOCK_TYPE]
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
    def get_headline_blocks_from_chart_blocks(
        cls, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
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
