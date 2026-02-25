from unittest import mock

from draftjs_exporter.dom import DOM
from wagtail.admin.site_summary import SummaryItem
from wagtail.models import Page

from cms.dashboard import wagtail_hooks
from cms.dashboard.wagtail_hooks import _build_link_props, link_entity_with_href

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
    expected_value = (
        f'<link rel="stylesheet" type="text/css" href="{returned_static_css_theme}">'
    )
    assert global_admin_css_link == expected_value


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


def test_construct_page_action_menu_inserts_preview_action():
    """
    Given a composite page and an empty page action menu
    When the ``add_frontend_preview_action`` hook is called
    Then a preview action is prepended with the expected redirect URL
    """
    from tests.fakes.factories.cms.composite_page_factory import (
        FakeCompositePageFactory,
    )

    # Given
    # Build a fake page with pk so reverse() works.
    page = FakeCompositePageFactory.build_blank_page(slug="foo")
    page.pk = 99
    menu_items: list = []
    request = mock.Mock()
    context = {"page": page}

    # When
    wagtail_hooks.add_frontend_preview_action(menu_items, request, context)

    # Then
    assert menu_items, "hook should add at least one item"
    first = menu_items[0]
    # Verify it is an action item with our name and correct URL.
    assert first.name == "action-preview"
    assert "/preview-to-frontend/99/" in first.get_url(context)


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


@mock.patch(f"{MODULE_PATH}.link_entity_with_href")
def test_register_link_props(spy_link_entity_with_href: mock.MagicMock):
    """
    Given no input
    When the wagtail hook `register_link_props` is called
    Then the `link_entity_with_href()` function
        is set on the link entity decorators
        via the `register_converter_rule()` call
    """
    # Given
    fake_rule = {"to_database_format": {"entity_decorators": {"LINK": {}}}}
    fake_converter_rules = {"contentstate": {"link": fake_rule}}
    spy_features = mock.MagicMock()
    spy_features.converter_rules_by_converter = fake_converter_rules

    # When
    wagtail_hooks.register_link_props(features=spy_features)

    # Then
    assert (
        fake_rule["to_database_format"]["entity_decorators"]["LINK"]
        == spy_link_entity_with_href
    )


class TestLinkEntityWithHref:
    @mock.patch.object(DOM, "create_element")
    @mock.patch(f"{MODULE_PATH}._build_link_props")
    def test_delegates_calls(
        self,
        spy_build_link_props: mock.MagicMock,
        spy_dom_create_element: mock.MagicMock,
    ):
        """
        Given props containing a URL and children elements
        When `link_entity_with_href()` is called
        Then the call is delegated
            to `_build_link_props()` to make the initial props
            which are then passed to `DOM.create_element()`
        """
        # Given
        mocked_children = mock.Mock()
        fake_props = {"url": "https://abc.com", "children": mocked_children}

        # When
        link_entity_with_href(props=fake_props)

        # Then
        spy_build_link_props.assert_called_once_with(props=fake_props)
        spy_dom_create_element.assert_called_once_with(
            "a", spy_build_link_props.return_value, mocked_children
        )


class TestBuildLinkProps:
    @mock.patch.object(Page, "objects")
    def test_build_link_props_with_valid_page_id(
        self, mocked_page_model_manager: mock.MagicMock
    ):
        """
        Given a valid ID for a `Page` object
        When `_build_link_props()` is called
        Then the returned props
            also contain the page full URL
        """
        # Given
        page_id = 1
        expected_url = "https://test-ukhsa-dashboard.com/covid-19"
        mocked_page = mock.Mock()
        mocked_page.specific.full_url = expected_url
        mocked_page_model_manager.get.return_value = mocked_page

        # When
        link_props = _build_link_props({"id": page_id})

        # Then
        mocked_page_model_manager.get.assert_called_once_with(id=page_id)
        expected_props = {"linktype": "page", "id": page_id, "href": expected_url}
        assert link_props == expected_props

    @mock.patch(f"{MODULE_PATH}.check_url")
    def test_build_link_props_with_url(self, spy_check_url: mock.MagicMock):
        """
        Given a URL for a `Page` object
        When `_build_link_props()` is called
        Then the returned props
            contain only the page URL
        """
        # Given
        url = "https://test-ukhsa-dashboard.com/covid-19"
        spy_check_url.return_value = url

        # When
        link_props = _build_link_props(props={"url": url})

        # Then the correct link properties are returned
        expected_props = {"href": url}
        assert link_props == expected_props
        spy_check_url.assert_called_once_with(url_string=url)

    @mock.patch.object(Page, "objects")
    def test_build_link_props_for_non_existent_page(
        self, mocked_page_manager: mock.MagicMock
    ):
        """
        Given a `Page` object which does not exist
        When `_build_link_props()` is called
        Then the returned props
            contains an empty string for the URL
        """
        # Given
        mocked_page_manager.get.side_effect = Page.DoesNotExist

        # When
        link_props = _build_link_props(props={"id": 123})

        # Then the correct link properties are returned
        expected_props = {"href": "", "id": 123, "linktype": "page"}
        assert link_props == expected_props
