import pytest
from unittest import mock
from django.core.exceptions import ValidationError
from wagtail.blocks import StreamValue

from cms.dynamic_content.global_filter.card import GlobalFilterCard
from cms.dynamic_content.sections import ContentCards
from cms.topic.models import TopicPage
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPage


class TestContentCards:
    @mock.patch.object(ContentCards, "_validate_dependant_blocks")
    @mock.patch("wagtail.blocks.StreamBlock.clean")
    def test_clean_delegates_calls_correctly(
        self,
        mocked_validate_dependant_blocks: mock.MagicMock,
        mocked_clean: mock.MagicMock,
    ):
        """
        Given an instance of `ContentCards`
        When the `clean` method is called
        Then it makes a call to the `_validate_dependant_blocks` method
        """
        # Given
        content_cards = ContentCards()
        mocked_blocks = (
            [
                mock.MagicMock(block_type="text_card"),
                mock.MagicMock(block_type="filter_linked_map"),
            ],
        )

        # When
        content_cards.clean(value=mocked_blocks)

        # Then
        mocked_validate_dependant_blocks.assert_called_once()

    def test_context_card_raise_validation_error(self):
        """
        Given an instance of `ContentCards`
        When `_validate_dependant_blocks` is called, with an invalid combination of blocks
        Then a `ValidationError` is raised.
        """
        # Given
        content_cards = ContentCards()
        mocked_blocks = [
            mock.MagicMock(block_type="text_card"),
            mock.MagicMock(block_type="filter_linked_map"),
        ]

        # When / Then
        with pytest.raises(ValidationError) as validation_error:
            content_cards._validate_dependant_blocks(value=mocked_blocks)

        assert (
            "The 'Filter linked map' is only available when using 'global filter card'."
            in str(validation_error.value)
        )
