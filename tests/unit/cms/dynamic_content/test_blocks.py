"""Unit tests for cms.dynamic_content.blocks."""

from unittest import mock
from django.core.exceptions import ValidationError

import pytest
from wagtail.blocks import StructBlock, StructValue

from cms.dynamic_content.blocks import PageLink, SourceLinkBlock


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


class TestPageLinkBlock:
    """Tests for PageLink.get_api_representation()."""

    def test_no_page_returns_unauthorised(self):
        """
        Given a value with no page set
        When get_api_representation() is called
        Then the response is unauthorised and fields are blanked.
        """
        block = PageLink()
        value = {
            "title": "Test title",
            "sub_title": "Test subtitle",
            "page": None,
        }

        result = block.get_api_representation(value=value, context={})

        assert result["is_authorised"] is False
        assert result["title"] == ""
        assert result["sub_title"] == ""
        assert result["page"] == ""

    def test_public_page_is_always_authorised(self):
        """
        Given a public page
        When get_api_representation() is called
        Then the response is authorised and fields are preserved.
        """
        block = PageLink()

        mock_page = mock.MagicMock()
        mock_page.specific = mock_page
        mock_page.is_public = True

        value = {
            "title": "Test title",
            "sub_title": "Test subtitle",
            "page": mock_page,
        }

        result = block.get_api_representation(value=value, context={})

        assert result["is_authorised"] is True
        assert result["title"] == "Test title"
        assert result["sub_title"] == "Test subtitle"

    @mock.patch("cms.dynamic_content.blocks.check_page_permissions")
    def test_non_public_page_permission_denied(self, mock_check_permissions):
        """
        Given a non-public page and permissions are denied
        When get_api_representation() is called
        Then the response is unauthorised and fields are blanked.
        """
        mock_check_permissions.return_value = False

        block = PageLink()

        mock_page = mock.MagicMock()
        mock_page.specific = mock_page
        mock_page.is_public = False
        mock_page.theme = 1
        mock_page.sub_theme = 2
        mock_page.topic = 3

        mock_user = mock.MagicMock()
        mock_user.permission_sets = mock.MagicMock()
        mock_user.permission_sets = {"permission_sets": []}

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        value = {
            "title": "Test title",
            "sub_title": "Test subtitle",
            "page": mock_page,
        }

        context = {"request": mock_request}

        result = block.get_api_representation(value=value, context=context)

        assert result["is_authorised"] is False
        assert result["title"] == ""
        assert result["sub_title"] == ""
        assert result["page"] == ""

        mock_check_permissions.assert_called_once()

    @mock.patch("cms.dynamic_content.blocks.check_page_permissions")
    def test_non_public_page_permission_granted(self, mock_check_permissions):
        """
        Given a non-public page and permissions are granted
        When get_api_representation() is called
        Then the response is authorised and fields are preserved.
        """
        mock_check_permissions.return_value = True

        block = PageLink()

        mock_page = mock.MagicMock()
        mock_page.specific = mock_page
        mock_page.is_public = False
        mock_page.theme = 1
        mock_page.sub_theme = 2
        mock_page.topic = 3
        mock_page.full_url = "https://test-page-url"

        mock_user = mock.MagicMock()
        mock_user.permission_sets = mock.MagicMock()
        mock_user.permission_sets = {"permission_sets": []}

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        value = {
            "title": "Test title",
            "sub_title": "Test subtitle",
            "page": mock_page,
        }

        context = {"request": mock_request}

        result = block.get_api_representation(value=value, context=context)

        assert result["is_authorised"] is True
        assert result["title"] == "Test title"
        assert result["sub_title"] == "Test subtitle"
        assert result["page"] == "https://test-page-url"

        mock_check_permissions.assert_called_once()

    @mock.patch("cms.dynamic_content.blocks.check_page_permissions")
    def test_non_public_page_missing_request(self, mock_check_permissions):
        """
        Given a non-public page and no request in context
        When get_api_representation() is called
        Then the response is unauthorised and fields are blanked.
        """
        mock_check_permissions.return_value = False

        block = PageLink()

        mock_page = mock.MagicMock()
        mock_page.specific = mock_page
        mock_page.is_public = False
        mock_page.theme = 1
        mock_page.sub_theme = 2
        mock_page.topic = 3

        value = {
            "title": "Test title",
            "sub_title": "Test subtitle",
            "page": mock_page,
        }

        result = block.get_api_representation(value=value, context={})

        assert result["is_authorised"] is False
        assert result["title"] == ""
        assert result["sub_title"] == ""
        assert result["page"] == ""

        mock_check_permissions.assert_called_once()
