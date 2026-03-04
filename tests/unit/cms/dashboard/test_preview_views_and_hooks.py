from unittest import mock
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
        self,
        pk=1,
        slug="foo",
        can_edit=True,
        has_unpublished_changes=True,
        live=False,
    ):
        self.pk = pk
        self.slug = slug
        self._can_edit = can_edit
        self.has_unpublished_changes = has_unpublished_changes
        self.live = live
        self.specific_class = self.__class__

    @property
    def specific(self):
        # emulate Wagtail's .specific returning itself for fakes
        return self

    def permissions_for_user(self, user):
        return DummyPerms(self._can_edit)


class TestFrontendPreviewButton:
    def test_non_edit_view_returns_empty(self):
        """
        Given a page and a non-edit view name
        When `frontend_preview_button()` is called
        Then an empty list is returned
        """
        # Given
        page = FakePage()

        # When
        buttons = wagtail_hooks.frontend_preview_button(
            page=page,
            user=None,
            next_url=None,
            view_name="index",
        )

        # Then
        assert buttons == []

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_fallback_uses_template(
        self,
        spy_reverse: mock.MagicMock,
        settings,
    ):
        """
        Given URL reversing fails and a frontend template setting exists
        When `frontend_preview_button()` is called for a preview-enabled page
        Then the fallback frontend template URL is used

        Patches:
            `spy_reverse`: To force the fallback URL path
        """
        # Given
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

        # When
        buttons = wagtail_hooks.frontend_preview_button(
            page=page,
            user=None,
            next_url=None,
            view_name="edit",
        )

        # Then
        assert isinstance(buttons, list) and buttons
        button = buttons[0]
        assert isinstance(button, Button)
        assert button.label == "Preview"
        assert button.url == "https://frontend.test/preview?slug=bar"
        assert button.attrs["target"] == "_blank"
        assert button.attrs["rel"] == "noopener noreferrer"

    def test_live_non_draft_page_label_is_view_live(self):
        """
        Given a preview-enabled page with a live version and no draft changes
        When `frontend_preview_button()` is called
        Then the button label is `View Live`
        """
        # Given
        page = SimpleNamespace(
            pk=123,
            slug="bar",
            custom_preview_enabled=True,
            has_unpublished_changes=False,
            live=True,
        )

        # When
        buttons = wagtail_hooks.frontend_preview_button(
            page=page,
            user=None,
            next_url=None,
            view_name="edit",
        )

        # Then
        assert isinstance(buttons, list) and buttons
        assert buttons[0].label == "View Live"

    def test_page_with_no_draft_and_no_live_has_no_button(self):
        """
        Given a preview-enabled page with neither draft nor live version
        When `frontend_preview_button()` is called
        Then no button is returned
        """
        # Given
        page = SimpleNamespace(
            pk=123,
            slug="bar",
            custom_preview_enabled=True,
            has_unpublished_changes=False,
            live=False,
        )

        # When
        buttons = wagtail_hooks.frontend_preview_button(
            page=page,
            user=None,
            next_url=None,
            view_name="edit",
        )

        # Then
        assert buttons == []

    def test_non_enabled_page_returns_empty(self):
        """
        Given a page type that is not preview-enabled
        When `frontend_preview_button()` is called
        Then an empty list is returned
        """
        # Given
        page = FakePage(pk=123, slug="bar")

        # When
        buttons = wagtail_hooks.frontend_preview_button(
            page=page,
            user=None,
            next_url=None,
            view_name="edit",
        )

        # Then
        assert buttons == []


class TestPreviewToFrontendRedirectView:
    def test_build_route_slug_uses_nested_page_path_when_available(self):
        """
        Given a page with nested route path
        When route slug is built for preview URL
        Then nested path format is returned instead of leaf slug
        """
        # Given
        page = SimpleNamespace(
            slug="covid-19",
            get_url_parts=lambda request=None: (
                1,
                "https://frontend.test",
                "/respiratory-viruses/covid-19/",
            ),
        )

        # When
        route_slug = PreviewToFrontendRedirectView.build_route_slug(page=page)

        # Then
        assert route_slug == "respiratory-viruses/covid-19"

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_permission_denied(self, spy_get_object_or_404: mock.MagicMock):
        """
        Given a page for which the user cannot edit
        When `PreviewToFrontendRedirectView.get()` is called
        Then `PermissionDenied` is raised

        Patches:
            `spy_get_object_or_404`: To return a non-editable fake page
        """
        # Given
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="s", can_edit=False)
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()

        # When / Then
        with pytest.raises(PermissionDenied):
            view.get(request=request, pk=1)

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects(
        self,
        spy_get_object_or_404: mock.MagicMock,
        settings,
    ):
        """
        Given an editable page and a preview URL template
        When `PreviewToFrontendRedirectView.get()` is called
        Then the response redirects to the frontend with a token query parameter

        Patches:
            `spy_get_object_or_404`: To return an editable fake page
        """
        # Given
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        settings.PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE = (
            "https://frontend.test/preview?slug={slug}&t={token}"
        )
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()

        # When
        response = view.get(request=request, pk=1)

        # Then
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith("https://frontend.test/preview?slug=cover&t=")

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_with_nested_route_slug(
        self,
        spy_get_object_or_404: mock.MagicMock,
        settings,
    ):
        """
        Given an editable page with nested route path
        When preview redirect is generated
        Then URL uses nested route slug in `slug` query parameter

        Patches:
            `spy_get_object_or_404`: To return editable page with nested path.
        """
        # Given
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

        # When
        response = view.get(request=request, pk=1)

        # Then
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith(
            "https://frontend.test/preview?slug=respiratory-viruses%2Fcovid-19&t="
        )

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_normalises_legacy_query_params(
        self,
        spy_get_object_or_404: mock.MagicMock,
        settings,
    ):
        """
        Given a legacy preview URL template containing old query params
        When `PreviewToFrontendRedirectView.get()` is called
        Then the redirect URL is normalized to only `slug` and `t`

        Patches:
            `spy_get_object_or_404`: To return an editable fake page
        """
        # Given
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        settings.PAGE_PREVIEWS_FRONTEND_URL_TEMPLATE = "https://frontend.test/preview?page_id={page_id}&slug_name={slug_name}&draft=true&t={token}"
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()

        # When
        response = view.get(request=request, pk=1)

        # Then
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith("https://frontend.test/preview?slug=cover&t=")
        assert "draft=true" not in location
        assert "page_id=" not in location
        assert "slug_name=" not in location


class TestAddFrontendPreviewAction:
    def test_missing_page_or_pk_returns_none(self):
        """
        Given missing or unsaved page context
        When `add_frontend_preview_action()` is called
        Then no action is added
        """
        # Given
        request = None

        # When
        menu_items = []
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=request,
            context={},
        )

        menu_items_for_unsaved_page = []
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items_for_unsaved_page,
            request=request,
            context={"page": FakePage(pk=None)},
        )

        # Then
        assert menu_items == []
        assert menu_items_for_unsaved_page == []

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_exception_from_reverse_is_handled(
        self,
        spy_reverse: mock.MagicMock,
    ):
        """
        Given a preview-enabled page and reverse raises an exception
        When `add_frontend_preview_action()` is called
        Then no menu item is added

        Patches:
            `spy_reverse`: To simulate URL generation failure
        """
        # Given
        spy_reverse.side_effect = RuntimeError("reverse failed")
        menu_items = []

        # request.user.pk == 5
        request = SimpleNamespace(user=SimpleNamespace(pk=5))
        context = {
            "page": SimpleNamespace(
                pk=1,
                slug="test",
                custom_preview_enabled=True,
                has_unpublished_changes=True,
                live=False,
            )
        }

        # When
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=request,
            context=context,
        )

        # Then
        assert menu_items == []

    def test_insert_exception_is_handled(self):
        """
        Given a menu collection that raises on `insert`
        When `add_frontend_preview_action()` is called
        Then the function does not raise
        """

        # Given
        class BadMenuItems(list):
            def insert(self, index, item):
                raise RuntimeError("insert failed")

        menu_items = BadMenuItems()
        # request.user.pk == 5
        request = SimpleNamespace(user=SimpleNamespace(pk=5))
        context = {
            "page": SimpleNamespace(
                pk=1,
                slug="test",
                custom_preview_enabled=True,
                has_unpublished_changes=True,
                live=False,
            )
        }

        # When
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=request,
            context=context,
        )

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

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_get_preview_admin_url_returns_none_when_reverse_fails(
        self,
        spy_reverse: mock.MagicMock,
    ):
        """
        Given reverse fails for preview admin URL
        When preview admin URL is requested
        Then None is returned

        Patches:
            `spy_reverse`: To raise URL reversal failure.
        """
        spy_reverse.side_effect = NoReverseMatch("no reverse")
        page = SimpleNamespace(pk=1, custom_preview_enabled=True)
        assert wagtail_hooks._get_preview_admin_url(page=page) is None

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_build_view_live_url_uses_preview_redirect_for_preview_enabled_page(
        self,
        spy_reverse: mock.MagicMock,
    ):
        """
        Given a preview-enabled page
        When the publish-dialog live URL is built
        Then the preview redirect URL is used

        Patches:
            `spy_reverse`: To provide deterministic admin preview URL
        """
        # Given
        spy_reverse.return_value = "/cms-admin/preview-to-frontend/77/"
        page = SimpleNamespace(pk=77, custom_preview_enabled=True, url="/legacy-live/")

        # When
        live_url = wagtail_hooks._build_view_live_url(page=page)

        # Then
        assert live_url == "/cms-admin/preview-to-frontend/77/"

    def test_build_view_live_url_falls_back_to_page_url_for_non_preview_enabled_page(
        self,
    ):
        """
        Given a page that is not preview-enabled
        When the publish-dialog live URL is built
        Then the page live URL is used
        """
        # Given
        page = SimpleNamespace(pk=77, custom_preview_enabled=False, url="/legacy-live/")

        # When
        live_url = wagtail_hooks._build_view_live_url(page=page)

        # Then
        assert live_url == "/legacy-live/"

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
    @mock.patch(
        f"{MODULE_PATH}.dashboard.wagtail_hooks._ORIGINAL_CREATE_VIEW_LIVE_MESSAGE_BUTTON"
    )
    def test_patched_create_view_live_message_button_falls_back_when_no_url(
        self,
        spy_original: mock.MagicMock,
        spy_build_view_live_url: mock.MagicMock,
    ):
        """
        Given no resolved live URL
        When patched create view button builder runs
        Then original wagtail implementation is used

        Patches:
            `spy_original`: To assert fallback path is used.
            `spy_build_view_live_url`: To force missing live URL.
        """
        spy_build_view_live_url.return_value = None
        fake_view = SimpleNamespace(page=SimpleNamespace(pk=1))

        wagtail_hooks._patched_create_view_live_message_button(fake_view)

        spy_original.assert_called_once_with(fake_view)

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

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks._build_view_live_url")
    @mock.patch(
        f"{MODULE_PATH}.dashboard.wagtail_hooks._ORIGINAL_EDIT_VIEW_LIVE_MESSAGE_BUTTON"
    )
    def test_patched_edit_view_live_message_button_falls_back_when_no_url(
        self,
        spy_original: mock.MagicMock,
        spy_build_view_live_url: mock.MagicMock,
    ):
        """
        Given no resolved live URL
        When patched edit view button builder runs
        Then original wagtail implementation is used

        Patches:
            `spy_original`: To assert fallback path is used.
            `spy_build_view_live_url`: To force missing live URL.
        """
        spy_build_view_live_url.return_value = None
        fake_view = SimpleNamespace(page=SimpleNamespace(pk=1))

        wagtail_hooks._patched_edit_view_live_message_button(fake_view)

        spy_original.assert_called_once_with(fake_view)


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
