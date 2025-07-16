import pytest
from unittest import mock
from django.core.exceptions import ValidationError

from cms.dynamic_content.sections import ContentCards


class TestContentCards:
    @mock.patch.object(ContentCards, "_validate_dependant_blocks")
    @mock.patch("wagtail.blocks.StreamBlock.clean")
    def test_clean_delegates_calls_correctly(
        self,
        spy_parent_clean_method: mock.MagicMock,
        mocked_validate_dependant_blocks: mock.MagicMock,
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
        returned_value = content_cards.clean(value=mocked_blocks)

        # Then
        mocked_validate_dependant_blocks.assert_called_once()
        assert returned_value == spy_parent_clean_method.return_value

    @pytest.mark.parametrize(
        "filter_linked_block_type",
        (
            "filter_linked_map",
            "filter_linked_sub_plot_chart_template",
            "filter_linked_time_series_chart_template",
        ),
    )
    def test_raises_validation_error_when_filter_linked_component_used_without_global_filter(
        self, filter_linked_block_type: str
    ):
        """
        Given an instance of `ContentCards`
        When `_validate_dependant_blocks` is called, with an invalid combination of blocks
        Then a `ValidationError` is raised.
        """
        # Given
        content_cards = ContentCards()
        mocked_blocks = [
            mock.MagicMock(block_type="text_card"),
            mock.MagicMock(block_type=filter_linked_block_type),
        ]

        # When / Then
        with pytest.raises(ValidationError) as validation_error:
            content_cards._validate_dependant_blocks(value=mocked_blocks)

        readable_name = filter_linked_block_type.replace("_", " ")
        assert (
            f"The '{readable_name}' is only available when using 'global filter card'."
            in str(validation_error.value)
        )

    @pytest.mark.parametrize(
        "filter_linked_block_type",
        (
            "filter_linked_map",
            "filter_linked_sub_plot_chart_template",
            "filter_linked_time_series_chart_template",
        ),
    )
    def test_no_error_is_raised_when_filter_linked_component_used_with_global_filter(
        self, filter_linked_block_type: str
    ):
        """
        Given an instance of `ContentCards`
        When `_validate_dependant_blocks` is called,
            with a valid combination of blocks
        Then no error is raised.
        """
        # Given
        content_cards = ContentCards()
        mocked_blocks = [
            mock.MagicMock(block_type="global_filter_card"),
            mock.MagicMock(block_type=filter_linked_block_type),
        ]

        # When / Then
        content_cards._validate_dependant_blocks(value=mocked_blocks)
