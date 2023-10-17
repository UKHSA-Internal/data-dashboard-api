from unittest import mock

from wagtail.admin.site_summary import SummaryItem

from cms.dashboard import wagtail_hooks

MODULE_PATH = "cms.dashboard.wagtail_hooks"


@mock.patch(f"{MODULE_PATH}.static")
def test_global_admin_css(mocked_static: mock.MagicMock):
    """
    Given no input
    When the wagtail hook `global_admin_css()` is called
    Then the correct global admin CSS link is returned

    Patches:
        `mocked_static`: To isolate the return value
            of the `static` function call and remove
            the need of having to collect static files
            for the test run

    """
    # Given / When
    returned_static_css_theme = "fake-css-theme-static-location"
    mocked_static.return_value = returned_static_css_theme
    global_admin_css_link: str = wagtail_hooks.global_admin_css()

    # Then
    assert global_admin_css_link.startswith('<link rel="stylesheet" type="text/css"')
    assert returned_static_css_theme in global_admin_css_link


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
    class FakeMenuItem:
        def __init__(self, name):
            self.name = name

    core_menu_items = [
        FakeMenuItem(name="images"),
        FakeMenuItem(name="documents"),
        FakeMenuItem("pages"),
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
    wagtail_hooks.update_summary_items(
        request=mock_request, summary_items=core_summary_items
    )

    # Then
    assert len(core_summary_items) == 1
    assert core_summary_items[0].request == mock_request
    assert isinstance(core_summary_items[0], SummaryItem)
