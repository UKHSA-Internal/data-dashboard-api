from unittest import mock

from wagtail.admin.site_summary import PagesSummaryItem

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
    class MenuItem:
        def __init__(self, name):
            self.name = name

    core_menu_items = [MenuItem("images"), MenuItem("documents"), MenuItem("pages")]

    # When
    wagtail_hooks.hide_default_menu_items(mock.Mock(), core_menu_items)

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

    # When
    edited_summary_items = wagtail_hooks.update_summary_items(
        mock.Mock(), core_summary_items
    )

    # Then
    assert len(edited_summary_items) == 1
    assert isinstance(edited_summary_items[0], PagesSummaryItem)
