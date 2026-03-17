import pytest
import unittest.mock as mock
from types import SimpleNamespace
from django.core.exceptions import PermissionDenied
from django.urls import NoReverseMatch
from django.test import RequestFactory
from wagtail.admin.widgets import Button
from cms.dashboard import wagtail_hooks
from cms.dashboard.views import PreviewToFrontendRedirectView

MODULE_PATH = "cms"


class TestAddFrontendPreviewActionExceptions:
    @mock.patch("cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView")
    @mock.patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch)
    def test_no_reverse_match_fallback_template(self, mock_reverse, mock_view):
        """
        Given reverse raises NoReverseMatch
        When add_frontend_preview_action is called
        Then fallback template is used and menu_items is updated
        """
        page = SimpleNamespace(
            pk=1,
            slug="slug",
            custom_preview_enabled=True,
            has_unpublished_changes=True,
            live=False,
        )
        menu_items = []
        # Patch build_route_slug to return a known slug
        mock_view.build_route_slug.return_value = "slug"
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings",
            PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE="http://test/{slug}",
            PAGE_PREVIEWS_ENABLED=True,
        ):
            wagtail_hooks.add_frontend_preview_action(menu_items, None, {"page": page})
        assert menu_items and menu_items[0].label == "Preview"


import pytest
import unittest.mock as mock
from types import SimpleNamespace
from django.core.exceptions import PermissionDenied
from django.urls import NoReverseMatch
from django.test import RequestFactory
from wagtail.admin.widgets import Button
from cms.dashboard import wagtail_hooks
from cms.dashboard.views import PreviewToFrontendRedirectView

MODULE_PATH = "cms"


import unittest.mock as mock
import unittest.mock as mock
from types import SimpleNamespace
import pytest
from django.core.exceptions import PermissionDenied
from django.urls import NoReverseMatch
from django.test import RequestFactory
from wagtail.admin.widgets import Button
from cms.dashboard import wagtail_hooks
from cms.dashboard.views import PreviewToFrontendRedirectView

MODULE_PATH = "cms"


class DummyPerms:
    def __init__(self, can_edit):
        self._can_edit = can_edit

    def can_edit(self):
        return self._can_edit


class FakePage:
    custom_preview_enabled = False

    def __init__(
        self, pk=1, slug="foo", can_edit=True, has_unpublished_changes=True, live=False
    ):
        self.pk = pk
        self.slug = slug
        self._can_edit = can_edit

        self.has_unpublished_changes = has_unpublished_changes
        self.live = live
        self.specific_class = self.__class__

    @property
    def specific(self):
        return self

    def permissions_for_user(self, user):
        return DummyPerms(self._can_edit)


class TestFrontendPreviewButton:
    def test_non_edit_view_returns_empty(self):
        page = FakePage()
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="index"
        )
        assert buttons == []

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_fallback_uses_template(self, spy_reverse: mock.MagicMock, settings):
        spy_reverse.side_effect = NoReverseMatch("no reverse")
        settings.PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE = (
            "https://frontend.test/preview?slug={slug}"
        )
        page = SimpleNamespace(
            pk=123,
            slug="bar",
            custom_preview_enabled=True,
            has_unpublished_changes=True,
            live=False,
        )
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="edit"
        )
        assert isinstance(buttons, list) and buttons
        button = buttons[0]

        assert isinstance(button, Button)
        assert button.label == "Preview"
        assert button.url == "https://frontend.test/preview?slug=bar"
        assert button.attrs["target"] == "_blank"
        assert button.attrs["rel"] == "noopener noreferrer"

    def test_live_non_draft_page_label_is_view_live(self):
        page = SimpleNamespace(
            pk=123,
            slug="bar",
            custom_preview_enabled=True,
            has_unpublished_changes=False,
            live=True,
        )
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="edit"
        )
        assert isinstance(buttons, list) and buttons

        assert buttons[0].label == "View Live"

    def test_page_with_no_draft_and_no_live_has_no_button(self):
        page = SimpleNamespace(
            pk=123,
            slug="bar",
            custom_preview_enabled=True,
            has_unpublished_changes=False,
            live=False,
        )
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="edit"
        )

        assert buttons == []

    def test_non_enabled_page_returns_empty(self):
        page = FakePage(pk=123, slug="bar")
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="edit"
        )
        assert buttons == []


class TestPreviewToFrontendRedirectView:
    def test_build_route_slug_uses_nested_page_path_when_available(self):
        page = SimpleNamespace(
            slug="covid-19",
            get_url_parts=lambda request=None: (
                1,
                "https://frontend.test",
                "/respiratory-viruses/covid-19/",
            ),
        )
        route_slug = PreviewToFrontendRedirectView.build_route_slug(page=page)
        assert route_slug == "respiratory-viruses/covid-19"

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_permission_denied(self, spy_get_object_or_404: mock.MagicMock):
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="s", can_edit=False)

        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        with pytest.raises(PermissionDenied):
            view.get(request=request, pk=1)

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects(self, spy_get_object_or_404: mock.MagicMock, settings):
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        settings.PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE = (
            "https://frontend.test/preview?slug={slug}&t={token}"
        )
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")

        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith("https://frontend.test/preview?slug=cover&t=")

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_with_nested_route_slug(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        page = FakePage(pk=1, slug="covid-19", can_edit=True)
        page.get_url_parts = lambda request=None: (
            1,
            "https://frontend.test",
            "/respiratory-viruses/covid-19/",
        )
        spy_get_object_or_404.return_value = page
        settings.PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE = (
            "https://frontend.test/preview?slug={slug}&t={token}"
        )
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")

        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith(
            "https://frontend.test/preview?slug=respiratory-viruses%2Fcovid-19&t="
        )

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_normalises_legacy_query_params(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        settings.PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE = "https://frontend.test/preview?page_id={page_id}&slug_name={slug_name}&draft=true&t={token}"
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")

        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith("https://frontend.test/preview?slug=cover&t=")


class TestAddFrontendPreviewAction:
    def test_missing_page_or_pk_returns_none(self):
        request = None
        menu_items = []

        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items, request=request, context={}
        )
        menu_items_for_unsaved_page = []
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items_for_unsaved_page,
            request=request,
            context={"page": FakePage(pk=None)},
        )
        assert menu_items == []
        assert menu_items_for_unsaved_page == []

    def test_non_enabled_page_is_noop(self):
        """
        Given a page type that is not preview-enabled
        When `add_frontend_preview_action()` is called
        Then the menu remains unchanged
        """
        # Given
        menu_items = []
        # request.user.pk == 5
        request = SimpleNamespace(user=SimpleNamespace(pk=5))
        context = {"page": FakePage(pk=1, slug="test")}

        # When
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=request,
            context=context,
        )

        # Then
        assert menu_items == []

    @pytest.mark.parametrize(
        "custom_preview_enabled,has_unpublished_changes,live,should_have_action,expected_label",
        [
            (False, True, False, False, None),
            (True, True, False, True, "Preview"),
            (True, False, True, True, "View Live"),
            (True, False, False, False, None),
        ],
    )
    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_only_enabled_page_types_get_preview_actions(
        self,
        spy_reverse: mock.MagicMock,
        custom_preview_enabled,
        has_unpublished_changes,
        live,
        should_have_action,
        expected_label,
    ):
        """
        Given a page type with configured `custom_preview_enabled`
        When preview actions are constructed
        Then only enabled types receive preview button and menu actions

        Patches:
            `spy_reverse`: To provide a deterministic preview admin URL.
        """

        # Given
        page = SimpleNamespace(
            pk=42,
            slug="preview-target",
            custom_preview_enabled=custom_preview_enabled,
            has_unpublished_changes=has_unpublished_changes,
            live=live,
        )

        spy_reverse.side_effect = (
            lambda name, args=None: f"/admin/preview-to-frontend/{args[0]}/"
        )

        # When
        buttons = wagtail_hooks.frontend_preview_button(
            page=page,
            user=None,
            next_url=None,
            view_name="edit",
        )
        menu_items = []
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=None,
            context={"page": page},
        )

        # Then
        assert (len(buttons) > 0) is should_have_action
        assert (len(menu_items) > 0) is should_have_action
        if should_have_action:
            assert buttons[0].label == expected_label
            assert menu_items[0].label == expected_label


class TestPublishDialogViewLiveUrl:
    def test_get_preview_admin_url_returns_none_when_page_missing_or_unsaved(self):
        """

        Given missing page or page without primary key
        When preview admin URL is requested
        Then None is returned
        """
        assert wagtail_hooks._get_preview_admin_url(page=None) is None
        assert (
            wagtail_hooks._get_preview_admin_url(page=SimpleNamespace(pk=None)) is None
        )

    def test_get_preview_admin_url_returns_none_when_preview_not_enabled(self):
        """
        Given a page with preview disabled
        When preview admin URL is requested
        Then None is returned
        """
        page = SimpleNamespace(pk=1, custom_preview_enabled=False)
        assert wagtail_hooks._get_preview_admin_url(page=page) is None

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks._build_view_live_url")
    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.messages.button")
    def test_patched_create_view_live_message_button_uses_new_window(
        self,
        spy_messages_button: mock.MagicMock,
        spy_build_view_live_url: mock.MagicMock,
    ):
        """
        Given a resolved live URL
        When patched create view button builder runs
        Then it creates a View live button opening in a new window

        Patches:
            `spy_messages_button`: To assert button creation args.

            `spy_build_view_live_url`: To provide deterministic live URL.
        """
        spy_build_view_live_url.return_value = "/preview-url/"
        fake_view = SimpleNamespace(page=SimpleNamespace(pk=1))

        wagtail_hooks._patched_create_view_live_message_button(fake_view)

        spy_messages_button.assert_called_once_with(
            "/preview-url/", "View live", new_window=True
        )

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks._build_view_live_url")
    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.messages.button")
    def test_patched_edit_view_live_message_button_uses_new_window(
        self,
        spy_messages_button: mock.MagicMock,
        spy_build_view_live_url: mock.MagicMock,
    ):
        """
        Given a resolved live URL
        When patched edit view button builder runs
        Then it creates a View live button opening in a new window


        Patches:
            `spy_messages_button`: To assert button creation args.
            `spy_build_view_live_url`: To provide deterministic live URL.
        """
        spy_build_view_live_url.return_value = "/preview-url/"
        fake_view = SimpleNamespace(page=SimpleNamespace(pk=1))

        wagtail_hooks._patched_edit_view_live_message_button(fake_view)

        spy_messages_button.assert_called_once_with(
            "/preview-url/", "View live", new_window=True
        )


class TestCustomPreviewEnabled:
    def test_defaults_to_false_when_attribute_missing(self):
        """
        Given a page class without `custom_preview_enabled`
        When the page attribute is checked
        Then the page is not preview-enabled
        """
        # Given
        page = FakePage()

        # When
        is_preview_enabled = bool(getattr(page, "custom_preview_enabled", False))

        # Then
        assert not is_preview_enabled


class TestGetPreviewAdminUrl:
    def test_reverse_success(self):
        """
        Given a page with pk and custom_preview_enabled True,
        When _get_preview_admin_url is called and reverse succeeds,
        Then it returns the rrect URL.
        """
        from cms.dashboard.wagtail_hooks import _get_preview_admin_url
        import unittest.mock as mock

        page = SimpleNamespace(pk=123, custom_preview_enabled=True)
        with mock.patch(
            "cms.dashboard.wagtail_hooks.reverse", return_value="/preview/123/"
        ):
            assert _get_preview_admin_url(page) == "/preview/123/"

    def test_reverse_no_reverse_match(self):
        """
        Given a page with pk and custom_preview_enabled True,
        When _get_preview_admin_url is called and reverse raises NoReverseMatch,
        Then it returns None.
        """
        from cms.dashboard.wagtail_hooks import _get_preview_admin_url
        from django.urls import NoReverseMatch
        import unittest.mock as mock

        page = SimpleNamespace(pk=123, custom_preview_enabled=True)
        with mock.patch(
            "cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch()
        ):
            assert _get_preview_admin_url(page) is None

    def test_reverse_runtime_error(self):
        """
        Given a page with pk and custom_preview_enabled True,
        When _get_preview_admin_url is called and reverse raises RuntimeError,
        Then it returns None.
        """
        from cms.dashboard.wagtail_hooks import _get_preview_admin_url
        import unittest.mock as mock

        page = SimpleNamespace(pk=123, custom_preview_enabled=True)
        with mock.patch(
            "cms.dashboard.wagtail_hooks.reverse", side_effect=RuntimeError()
        ):
            assert _get_preview_admin_url(page) is None
