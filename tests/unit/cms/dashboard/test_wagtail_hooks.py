import pytest
import cms.dashboard.wagtail_hooks  # Ensure module is imported for coverage
from unittest import mock
from unittest.mock import Mock, patch, MagicMock
from django.urls import NoReverseMatch
from cms.dashboard.wagtail_hooks import _build_view_live_url, frontend_preview_button, add_frontend_preview_action, settings

class TestCoverageCompleteness:
    def test__insert_frontend_preview_action(self):
        """
        Given a menu_items list and a page
        When _insert_frontend_preview_action is called
        Then it inserts a FrontendPreviewAction with the correct URL and label
        """
        from cms.dashboard.wagtail_hooks import _insert_frontend_preview_action
        page = mock.Mock()
        page.pk = 888
        menu_items = []
        with mock.patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/888"):
            with mock.patch("cms.dashboard.wagtail_hooks.FrontendPreviewAction", side_effect=lambda **kwargs: type('FPA', (), kwargs)()):
                _insert_frontend_preview_action(menu_items, page, "Preview")
                assert len(menu_items) == 1
                assert getattr(menu_items[0], "url", None) == "/admin/preview/888"
        """
        Given label 'View Live' and live_url is falsy
        When frontend_preview_button is called and reverse raises NoReverseMatch
        Then it returns a Button with the preview URL from the template
        """
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        from django.urls import NoReverseMatch
        page = mock.Mock()
        page.pk = 123
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True, PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE="http://tpl/{slug}"):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="View Live"):
                with mock.patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None):
                    with mock.patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch()):
                        with mock.patch("cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug", return_value="sluggy"):
                            with mock.patch("cms.dashboard.wagtail_hooks.Button", side_effect=lambda **kwargs: type('Btn', (), kwargs)()) as btn:
                                result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
                                assert len(result) == 1
                                assert getattr(result[0], "url", None) == "http://tpl/sluggy"

    def test_add_frontend_preview_action_preview_branch_template(self):
        """
        Given label 'Preview' and reverse raises NoReverseMatch
        When add_frontend_preview_action is called
        Then it inserts a FrontendPreviewAction with the preview URL from the template
        """
        from cms.dashboard.wagtail_hooks import add_frontend_preview_action
        from django.urls import NoReverseMatch
        page = mock.Mock()
        page.pk = 456
        menu_items = []
        context = {"page": page}
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True, PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE="http://tpl/{slug}"):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"):
                with mock.patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch()):
                    with mock.patch("cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug", return_value="sluggy"):
                        with mock.patch("cms.dashboard.wagtail_hooks.FrontendPreviewAction", side_effect=lambda **kwargs: type('FPA', (), kwargs)()):
                            add_frontend_preview_action(menu_items, request=None, context=context)
                            assert len(menu_items) == 1
                            assert getattr(menu_items[0], "url", None) == "http://tpl/sluggy"

    def test_frontend_preview_button_view_live_fallback_preview(self):
        """
        Given label 'View Live' and live_url is falsy
        When frontend_preview_button is called and reverse succeeds
        Then it returns a Button with the preview URL from reverse
        """
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        page = mock.Mock()
        page.pk = 42
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="View Live"):
                with mock.patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None):
                    with mock.patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/42"):
                        with mock.patch("cms.dashboard.wagtail_hooks.Button", side_effect=lambda **kwargs: type('Btn', (), kwargs)()) as btn:
                            result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
                            assert len(result) == 1
                            assert getattr(result[0], "url", None) == "/admin/preview/42"

    def test_add_frontend_preview_action_preview_branch(self):
        """
        Given label 'Preview' and reverse succeeds
        When add_frontend_preview_action is called
        Then it inserts a FrontendPreviewAction with the preview URL from reverse
        """
        from cms.dashboard.wagtail_hooks import add_frontend_preview_action
        page = mock.Mock()
        page.pk = 99
        menu_items = []
        context = {"page": page}
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"):
                with mock.patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/99"):
                    with mock.patch("cms.dashboard.wagtail_hooks.FrontendPreviewAction", side_effect=lambda **kwargs: type('FPA', (), kwargs)()):
                        add_frontend_preview_action(menu_items, request=None, context=context)
                        assert len(menu_items) == 1
                        assert getattr(menu_items[0], "url", None) == "/admin/preview/99"

    def test_add_frontend_preview_action_preview_branch_explicit(self):
        """
        Given label 'Preview' and reverse succeeds
        When add_frontend_preview_action is called
        Then it inserts a FrontendPreviewAction with the preview URL from reverse (explicit branch coverage)
        """
        from cms.dashboard.wagtail_hooks import add_frontend_preview_action
        page = mock.Mock()
        page.pk = 77
        menu_items = []
        context = {"page": page}
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"):
                with mock.patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/77"):
                    with mock.patch("cms.dashboard.wagtail_hooks.FrontendPreviewAction", side_effect=lambda **kwargs: type('FPA', (), kwargs)()):
                        add_frontend_preview_action(menu_items, request=None, context=context)
                        assert len(menu_items) == 1
                        assert getattr(menu_items[0], "url", None) == "/admin/preview/77"
    def test_add_frontend_preview_action_preview_branch(self):
        """
        Given label 'Preview' and reverse succeeds
        When add_frontend_preview_action is called
        Then it inserts a FrontendPreviewAction with the preview URL from reverse
        """
        from cms.dashboard.wagtail_hooks import add_frontend_preview_action
        page = mock.Mock()
        page.pk = 99
        menu_items = []
        context = {"page": page}
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"):
                with mock.patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/99"):
                    with mock.patch("cms.dashboard.wagtail_hooks.FrontendPreviewAction", side_effect=lambda **kwargs: type('FPA', (), kwargs)()):
                        add_frontend_preview_action(menu_items, request=None, context=context)
                        assert len(menu_items) == 1
                        assert getattr(menu_items[0], "url", None) == "/admin/preview/99"

    def test_frontend_preview_button_view_live_truthy_url(self):
        """Given label 'View Live' and live_url is truthy, When frontend_preview_button is called, Then it returns a Button with the live_url."""
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        page = mock.Mock()
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="View Live"):
                with mock.patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value="http://live"): 
                    with mock.patch("cms.dashboard.wagtail_hooks.Button", side_effect=lambda **kwargs: type('Btn', (), kwargs)()) as btn:
                        result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
                        assert len(result) == 1
                        assert getattr(result[0], "url", None) == "http://live"
    def test_frontend_preview_button_view_name_not_edit(self):
        """Given view_name is not 'edit', When frontend_preview_button is called, Then it returns []."""
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        page = mock.Mock()
        result = frontend_preview_button(page, user=None, next_url=None, view_name="not-edit")
        assert result == []

    def test_frontend_preview_button_previews_disabled(self):
        """Given PAGE_PREVIEWS_ENABLED is False, When frontend_preview_button is called, Then it returns []."""
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        page = mock.Mock()
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=False):
            result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
            assert result == []
    def test_get_preview_button_label_custom_preview_disabled(self):
        """Given a page with custom_preview_enabled False, When _get_preview_button_label is called, Then it returns None."""
        from cms.dashboard.wagtail_hooks import _get_preview_button_label
        page = mock.Mock()
        page.custom_preview_enabled = False
        assert _get_preview_button_label(page) is None

    
    def test_frontend_preview_button_view_live_falsy_url(self):
        """Given label 'View Live' and live_url is falsy, When frontend_preview_button is called, Then it returns a Button with fallback URL."""
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        from django.urls import NoReverseMatch
        page = mock.Mock()
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="View Live"):
                with mock.patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None):
                    with mock.patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch()):
                        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE="http://tpl/{slug}"):
                            with mock.patch("cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug", return_value="sluggy"):
                                result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
                                assert len(result) == 1
                                assert getattr(result[0], "url", None) == "http://tpl/sluggy"

    def test_add_frontend_preview_action_view_live_falsy_url(self):
        """Given label 'View Live' and live_url is falsy, When add_frontend_preview_action is called, Then it returns early (None)."""
        from cms.dashboard.wagtail_hooks import add_frontend_preview_action
        page = mock.Mock()
        page.pk = 1
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="View Live"):
                with mock.patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None):
                    menu_items = []
                    context = {"page": page}
                    result = add_frontend_preview_action(menu_items, None, context)
                    assert result is None
    def test_get_preview_admin_url_none_page(self):
        """Given None as page, When _get_preview_admin_url is called, Then it returns None."""
        from cms.dashboard.wagtail_hooks import _get_preview_admin_url
        assert _get_preview_admin_url(None) is None

    def test_get_preview_admin_url_no_pk(self):
        """Given a page without pk, When _get_preview_admin_url is called, Then it returns None."""
        from cms.dashboard.wagtail_hooks import _get_preview_admin_url
        page = mock.Mock()
        page.pk = None
        assert _get_preview_admin_url(page) is None

    def test_get_preview_admin_url_preview_disabled(self):
        """Given a page with custom_preview_enabled False, When _get_preview_admin_url is called, Then it returns None."""
        from cms.dashboard.wagtail_hooks import _get_preview_admin_url
        page = mock.Mock()
        page.pk = 1
        page.custom_preview_enabled = False
        assert _get_preview_admin_url(page) is None

    def test_get_preview_button_label_preview(self):
        """Given a page with draft, When _get_preview_button_label is called, Then it returns 'Preview'."""
        from cms.dashboard.wagtail_hooks import _get_preview_button_label
        page = mock.Mock()
        page.custom_preview_enabled = True
        page.has_unpublished_changes = True
        page.live = False
        assert _get_preview_button_label(page) == "Preview"

    def test_get_preview_button_label_view_live(self):
        """Given a page with live, When _get_preview_button_label is called, Then it returns 'View Live'."""
        from cms.dashboard.wagtail_hooks import _get_preview_button_label
        page = mock.Mock()
        page.custom_preview_enabled = True
        page.has_unpublished_changes = False
        page.live = True
        assert _get_preview_button_label(page) == "View Live"

    def test_get_preview_button_label_none(self):
        """Given a page with neither draft nor live, When _get_preview_button_label is called, Then it returns None."""
        from cms.dashboard.wagtail_hooks import _get_preview_button_label
        page = mock.Mock()
        page.custom_preview_enabled = True
        page.has_unpublished_changes = False
        page.live = False
        assert _get_preview_button_label(page) is None

    def test_build_view_live_url_exception_and_slug(self):
        """Given a page where get_url_parts raises AttributeError, When _build_view_live_url is called, Then it returns slug url or None."""
        from cms.dashboard.wagtail_hooks import _build_view_live_url
        page = mock.Mock()
        page.get_url_parts.side_effect = AttributeError()
        page.slug = "sluggy"
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_FRONTEND_BASE_URL="http://base"): 
            assert _build_view_live_url(page) == "http://base/sluggy"
        page.slug = ""
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_FRONTEND_BASE_URL="http://base"): 
            assert _build_view_live_url(page) == "http://base/"

    def test_frontend_preview_button_label_none(self):
        """Given _get_preview_button_label returns None, When frontend_preview_button is called, Then it returns []."""
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        page = mock.Mock()
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value=None):
                result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
                assert result == []

    def test_frontend_preview_button_view_live_no_url(self):
        """Given label 'View Live' but no live_url, When frontend_preview_button is called, Then fallback logic is used."""
        from cms.dashboard.wagtail_hooks import frontend_preview_button
        from django.urls import NoReverseMatch
        page = mock.Mock()
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="View Live"):
                with mock.patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None):
                    with mock.patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch()):
                        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE="http://tpl/{slug}"):
                            with mock.patch("cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug", return_value="sluggy"):
                                result = frontend_preview_button(page, user=None, next_url=None, view_name="edit")
                                assert result[0].url == "http://tpl/sluggy"

    def test_register_admin_urls(self):
        """Given nothing, When register_admin_urls is called, Then it returns a list with a re_path."""
        from cms.dashboard.wagtail_hooks import register_admin_urls
        result = register_admin_urls()
        assert isinstance(result, list)
        assert result

    def test_add_frontend_preview_action_early_returns(self):
        """Given missing or invalid page/context/settings, When add_frontend_preview_action is called, Then it returns early (None)."""
        from cms.dashboard.wagtail_hooks import add_frontend_preview_action
        # No page
        menu_items = []
        context = {}
        assert add_frontend_preview_action(menu_items, None, context) is None
        # No pk
        page = mock.Mock()
        page.pk = None
        context = {"page": page}
        assert add_frontend_preview_action(menu_items, None, context) is None
        # PAGE_PREVIEWS_ENABLED False
        page.pk = 1
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=False):
            assert add_frontend_preview_action(menu_items, None, {"page": page}) is None
        # button_label None
        with mock.patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True):
            with mock.patch("cms.dashboard.wagtail_hooks._get_preview_button_label", return_value=None):
                assert add_frontend_preview_action(menu_items, None, {"page": page}) is None

from draftjs_exporter.dom import DOM
from wagtail.admin.site_summary import SummaryItem
from wagtail.models import Page

from cms.dashboard import wagtail_hooks
from cms.dashboard.wagtail_hooks import _build_link_props, link_entity_with_href
from django.urls import NoReverseMatch
from cms.dashboard.wagtail_hooks import _get_preview_admin_url
from django.test import override_settings


from wagtail.admin.action_menu import ActionMenuItem

@pytest.fixture(autouse=True)
def disable_wagtail_hooks():
    """
    Replace wagtail.hooks.register with a no-op decorator so
    functions behave like normal Python functions in tests.
    """
    with patch("wagtail.hooks.register", lambda *a, **k: (lambda f: f)):
        yield

class TestPagePreviews:





    @patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value="http://localhost:3000/fake-path")
    def test_frontend_preview_action_get_url(self, mock_build_url):
        menu_items = []
        page = Mock(pk=123, custom_preview_enabled=True, has_unpublished_changes=False, live=True)
        context = {"page": page}
        with override_settings(PAGE_PREVIEWS_ENABLED=True):
            add_frontend_preview_action(menu_items, request=None, context=context)
        preview_item = menu_items[0]
        assert preview_item.get_url({}) == "http://localhost:3000/fake-path"


    def test_add_frontend_preview_action_get_url_called(self):
        menu_items = []

        # Mock a page with attributes that trigger "View Live"
        page = Mock()
        page.pk = 123
        page.custom_preview_enabled = True
        page.has_unpublished_changes = False
        page.live = True

        # Make get_url_parts return real strings
        page.get_url_parts.return_value = ("http", "localhost:3000", "fake-path")

        context = {"page": page}

        with override_settings(PAGE_PREVIEWS_ENABLED=True):
            add_frontend_preview_action(
                menu_items=menu_items,
                request=None,
                context=context
            )

        # There should now be a FrontendPreviewAction instance in menu_items
        assert menu_items, "Expected a menu item to be added"
        preview_item = menu_items[0]

        # Calling get_url hits the line: return self._url
        url = preview_item.get_url(parent_context={})
        assert url == "http://localhost:3000/fake-path"


    @patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value="http://localhost:3000/fake-path")
    def test_add_frontend_preview_action_get_url_called(self, mock_build_url):
        menu_items = []
        # Mock a page with attributes that trigger "View Live"
        page = Mock()
        page.pk = 123
        page.custom_preview_enabled = True
        page.has_unpublished_changes = False  # no draft
        page.live = True
        context = {"page": page}
        with override_settings(PAGE_PREVIEWS_ENABLED=True):
            add_frontend_preview_action(menu_items=menu_items, request=None, context=context)
        # There should now be a FrontendPreviewAction instance in menu_items
        preview_item = menu_items[0]
        # Calling get_url hits the line: return self._url
        url = preview_item.get_url(parent_context={})
        assert url == "http://localhost:3000/fake-path"

    def test_add_frontend_preview_action_disabled(self):
        """Given PAGE_PREVIEWS_ENABLED is False, When add_frontend_preview_action is called, Then menu_items remains empty.

                        @mock.patch(f"{MODULE_PATH}.link_entity_with_href")
                        @mock.patch(f"{MODULE_PATH}.static")
                        def test_register_link_props(self, mocked_static, spy_link_entity_with_href):
            PAGE_PREVIEWS_ENABLED is False, a page and empty menu_items
        When:
            add_frontend_preview_action is called
        Then:
            menu_items remains empty
        """
        # Given
        menu_items = []
        page = Mock()
        page.pk = 123
        page.custom_preview_enabled = True
        context = {"page": page}
        # When
        with override_settings(PAGE_PREVIEWS_ENABLED=False):
            add_frontend_preview_action(menu_items=menu_items, request=None, context=context)
        # Then
        assert menu_items == []

    @override_settings(PAGE_PREVIEWS_FRONTEND_BASE_URL="http://localhost:3000")
    def test_build_view_live_url_returns_base_url(self):
        """
        Given a page where get_url_parts raises AttributeError and slug is empty
        When _build_view_live_url is called
        Then it returns the PAGE_PREVIEWS_FRONTEND_BASE_URL with a trailing slash
        """
        # Given: a mock page with get_url_parts raising AttributeError and empty slug
        page = Mock()
        page.get_url_parts.side_effect = AttributeError()
        page.slug = ""

        # When: calling _build_view_live_url
        result = _build_view_live_url(page)

        # Then: the function returns the base url with trailing slash
        expected_url = settings.PAGE_PREVIEWS_FRONTEND_BASE_URL.rstrip("/") + "/"
        assert result == expected_url

    @override_settings(PAGE_PREVIEWS_FRONTEND_BASE_URL="http://localhost:3000")
    def test_build_view_live_url_hits_route_path_line(self):
        # Create a mock page
        page = Mock()
        page.slug = "my-page"
        page.get_url_parts.return_value = ("http", "example.com", "path/to/page")

        # Call the function
        result = _build_view_live_url(page)

        # The route path line should have been executed, so result includes the stripped path
        assert result == "http://localhost:3000/path/to/page"

    @pytest.mark.parametrize("exception", [NoReverseMatch, RuntimeError])
    def test_get_preview_admin_url_reverse_exception(self, exception):
        # Simple mock page
        page = MagicMock()
        page.pk = 123
        page.custom_preview_enabled = True

        # Patch 'reverse' in the **module where it is used**, not Django globally
        with patch("cms.dashboard.wagtail_hooks.reverse", side_effect=exception):
            result = _get_preview_admin_url(page)

        assert result is None


class TestWagtailHooksGeneral:
    @mock.patch("cms.dashboard.wagtail_hooks.static")
    def test_global_admin_css(self, mocked_static):
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

    def test_register_icons_returns_correct_list_of_icons(self):
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

    @mock.patch("cms.dashboard.wagtail_hooks.static")
    def test_hide_default_menu_items(self, mocked_static):
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

    def test_update_summary_items(self):
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

    @mock.patch("cms.dashboard.wagtail_hooks.link_entity_with_href")
    def test_register_link_props(self, spy_link_entity_with_href):
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
    @mock.patch("cms.dashboard.wagtail_hooks._build_link_props")
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

    @mock.patch("cms.dashboard.wagtail_hooks.check_url")
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
