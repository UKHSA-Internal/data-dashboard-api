"""Unit tests for cms.dynamic_content.blocks."""

from unittest import mock
from django.core.exceptions import ValidationError

import pytest
from wagtail.blocks import StructBlock, StructValue

from cms.dynamic_content.blocks import SourceLinkBlock


class TestSourceLinkBlockClean:
    """Tests for SourceLinkBlock.clean() and validation."""

    def test_clean_validates_when_neither_page_nor_external_url(self):
        """
        Given a value with neither page nor external_url set
        When clean() is called
        Then validation passes and parent clean() is called and its result returned.
        """
        block = SourceLinkBlock()
        value = {
            "link_display_text": "",
            "page": None,
            "external_url": "",
        }

        expected = block.clean(value)
        assert expected["page"] is None
        assert expected["external_url"] == ""

    def test_clean_raises_when_both_page_and_external_url(self):
        """
        Given a value with both page and external_url set
        When clean() is called
        Then ValidationError is raised with the expected message.
        """
        block = SourceLinkBlock()
        value = {
            "link_display_text": "",
            "page": 1,
            "external_url": "https://example.com",
        }

        with pytest.raises(ValidationError) as exc_info:
            block.clean(value)

        assert exc_info.value.message == "Use either page OR external_url, not both."

    @mock.patch.object(StructBlock, "clean")
    def test_clean_passes_when_only_page_set(self, mocked_super_clean: mock.MagicMock):
        """
        Given a value with only page set
        When clean() is called
        Then validation passes and parent clean() is called and its result returned.
        """
        block = SourceLinkBlock()
        value = {
            "link_display_text": "",
            "page": 1,
            "external_url": "",
        }
        expected_result = mock.MagicMock()
        mocked_super_clean.return_value = expected_result

        result = block.clean(value)

        mocked_super_clean.assert_called_once_with(value=value)
        assert result is expected_result

    @mock.patch.object(StructBlock, "clean")
    def test_clean_passes_when_only_external_url_set(
        self, mocked_super_clean: mock.MagicMock
    ):
        """
        Given a value with only external_url set
        When clean() is called
        Then validation passes and parent clean() is called and its result returned.
        """
        block = SourceLinkBlock()
        value = {
            "link_display_text": "",
            "page": None,
            "external_url": "https://example.com",
        }
        expected_result = mock.MagicMock()
        mocked_super_clean.return_value = expected_result

        result = block.clean(value)

        mocked_super_clean.assert_called_once_with(value=value)
        assert result is expected_result


class TestSourceLinkBlockValidateOnlyOneOfPageOrExternalUrl:
    """Tests for _validate_only_one_of_page_or_external_url class method."""

    def test_does_not_raise_when_neither_set(self):
        """Does not raise when neither page nor external_url are set."""
        value = StructValue(SourceLinkBlock(), [("page", None), ("external_url", "")])

        SourceLinkBlock._validate_only_one_of_page_or_external_url(value=value)

        assert value["page"] is None
        assert value["external_url"] == ""

    def test_raises_when_both_set(self):
        """Raises ValidationError when both page and external_url are set."""
        value = StructValue(
            SourceLinkBlock(),
            [("page", 1), ("external_url", "https://example.com")],
        )

        with pytest.raises(ValidationError) as exc_info:
            SourceLinkBlock._validate_only_one_of_page_or_external_url(value=value)

        assert exc_info.value.message == "Use either page OR external_url, not both."

    def test_does_not_raise_when_only_page_set(self):
        """Does not raise when only page is set."""
        value = StructValue(
            SourceLinkBlock(),
            [("page", 1), ("external_url", "")],
        )

        SourceLinkBlock._validate_only_one_of_page_or_external_url(value=value)

    def test_does_not_raise_when_only_external_url_set(self):
        """Does not raise when only external_url is set."""
        value = StructValue(
            SourceLinkBlock(),
            [("page", None), ("external_url", "https://example.com")],
        )

        SourceLinkBlock._validate_only_one_of_page_or_external_url(value=value)
