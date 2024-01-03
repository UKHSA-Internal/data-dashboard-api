from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


class CMSBlockParser:
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
