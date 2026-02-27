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

    def __init__(self, pk=1, slug="foo", can_edit=True):
        self.pk = pk
        self.slug = slug
        self._can_edit = can_edit
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
            "https://frontend.test/preview?page_id={page_id}"
        )
        page = SimpleNamespace(pk=123, slug="bar", custom_preview_enabled=True)

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
        assert button.url == "https://frontend.test/preview?page_id=123"

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
            "https://frontend.test/preview?page_id={page_id}&t={token}"
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
        assert location.startswith("https://frontend.test/preview?page_id=1&t=")


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
            "page": SimpleNamespace(pk=1, slug="test", custom_preview_enabled=True)
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
            "page": SimpleNamespace(pk=1, slug="test", custom_preview_enabled=True)
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
        "custom_preview_enabled",
        [False, True],
    )
    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_only_enabled_page_types_get_preview_actions(
        self,
        spy_reverse: mock.MagicMock,
        custom_preview_enabled,
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
        assert (len(buttons) > 0) is custom_preview_enabled
        assert (len(menu_items) > 0) is custom_preview_enabled


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
