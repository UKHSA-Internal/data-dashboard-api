from unittest import mock

from wagtail.admin.site_summary import PagesSummaryItem
from wagtail.documents.wagtail_hooks import DocumentsMenuItem

from cms.dashboard import wagtail_hooks


def test_register_icons_returns_correct_list_of_icons():
    """
    Given a list of icons
    When the wagtail hook `register_icons()` is called
    Then a list of icons is returned including the original icons
        as well as a list of additional custom icons
    """
    # Given
    original_icons = ["original_icon_1.svg", "original_icon_2.svg"]

    # When
    registered_icons = wagtail_hooks.register_icons(icons=original_icons)

    # Then
    expected_icons = original_icons + wagtail_hooks.ADDITIONAL_CUSTOM_ICONS
    assert registered_icons == expected_icons


def test_hide_default_menu_items():
    """
    Given a list of default core menu items (documents and images)
    When wagtail hook `hide_default_menu_items` is called
    Then a list of items is returned which excludes the `Docments` and `Images` items from
        the core library
    """

    # Given
    class FakeDocumentsMenuItem(DocumentsMenuItem):
        def __init__(self, name, url="mock_url"):
            super(DocumentsMenuItem, self).__init__(name, url)

    core_menu_items = [
        FakeDocumentsMenuItem(name="images"),
        FakeDocumentsMenuItem(name="documents"),
        FakeDocumentsMenuItem(name="pages"),
    ]

    # When
    wagtail_hooks.hide_default_menu_items(
        request=mock.Mock(), menu_items=core_menu_items
    )

    # Then
    assert len(core_menu_items) == 1
    assert core_menu_items[0].name == "pages"


def test_update_summary_items():
    """
    Given a list of three summary items (including documents and images)
    When wagtail hook update_summary_items is called
    Then the menu will be cleared and PageSummaryItem added
        Leaving the summary items with a length of 1
    """
    # Given
    core_summary_items = ["document", "image", "pages"]
    mock_request = mock.Mock()

    # When
    edited_summary_items: list[object] = wagtail_hooks.update_summary_items(
        request=mock_request, summary_items=core_summary_items
    )

    # Then
    assert len(edited_summary_items) == 1
    assert isinstance(edited_summary_items[0], PagesSummaryItem)

    with mock.patch.object(
        wagtail_hooks, "update_summary_items", wraps=wagtail_hooks.update_summary_items
    ) as mock_update_summary_items:
        wagtail_hooks.update_summary_items(
            request=mock_request, summary_items=core_summary_items
        )
        mock_update_summary_items.assert_called_with(
            request=mock_request, summary_items=core_summary_items
        )
