import pytest
from django.core.exceptions import PermissionDenied
from django.urls import NoReverseMatch
from django.test import RequestFactory

from wagtail.admin.widgets import Button

from cms.dashboard import wagtail_hooks
from cms.dashboard.views import PreviewToFrontendRedirectView
from cms.dashboard.management.commands.build_cms_site_helpers.pages import _add_page_to_parent

class DummyPerms:
    def __init__(self, can_edit):
        self._can_edit = can_edit

    def can_edit(self):
        return self._can_edit


class FakePage:
    def __init__(self, pk=1, slug="foo", can_edit=True):
        self.pk = pk
        self.slug = slug
        self._can_edit = can_edit

    @property
    def specific(self):
        # emulate Wagtail's .specific returning itself for fakes
        return self

    def permissions_for_user(self, user):
        return DummyPerms(self._can_edit)


def test_frontend_preview_button_non_edit_view_returns_empty():
    page = FakePage()
    buttons = wagtail_hooks.frontend_preview_button(page, None, None, view_name="index")
    assert buttons == []


def test_frontend_preview_button_fallback_uses_template(monkeypatch, settings):
    # cause reverse to raise so the fallback path is exercised
    def fake_reverse(name, args=None):
        raise NoReverseMatch("no reverse")

    monkeypatch.setattr(wagtail_hooks, "reverse", fake_reverse)

    # set a custom template in settings
    settings.FRONTEND_PREVIEW_URL_TEMPLATE = "https://frontend.test/preview?page_id={page_id}"

    page = FakePage(pk=123, slug="bar")

    buttons = wagtail_hooks.frontend_preview_button(page, None, None, view_name="edit")
    assert isinstance(buttons, list) and buttons, "should return a non-empty list"
    btn = buttons[0]
    assert isinstance(btn, Button)
    assert "https://frontend.test/preview?page_id=123" == btn.url


def test_preview_redirect_view_permission_denied(monkeypatch):
    # patch get_object_or_404 to return a FakePage that is not editable
    def fake_get_object_or_404(klass, pk):
        return FakePage(pk=pk, slug="s", can_edit=False)

    monkeypatch.setattr("cms.dashboard.views.get_object_or_404", fake_get_object_or_404)

    request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
    request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

    view = PreviewToFrontendRedirectView()

    with pytest.raises(PermissionDenied):
        view.get(request, pk=1)


def test_preview_redirect_view_success(monkeypatch, settings):
    # patch get_object_or_404 to return a FakePage that is editable
    def fake_get_object_or_404(klass, pk):
        return FakePage(pk=pk, slug="cover", can_edit=True)

    monkeypatch.setattr("cms.dashboard.views.get_object_or_404", fake_get_object_or_404)

    # set a known template so we can assert the redirect location
    settings.FRONTEND_PREVIEW_URL_TEMPLATE = "https://frontend.test/preview?page_id={page_id}&t={token}"

    request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
    request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

    view = PreviewToFrontendRedirectView()
    resp = view.get(request, pk=1)

    # response is an HttpResponseRedirect; ensure location contains expected values
    location = resp.url if hasattr(resp, "url") else resp.get("Location")
    assert location.startswith("https://frontend.test/preview?page_id=1&t=")


def test_construct_page_action_menu_missing_page():
    """Test that missing page or pk in context is handled gracefully."""
    # Test with missing page
    menu_items = []
    context = {}
    request = None

    # Should return None gracefully, not raise
    result = wagtail_hooks.add_frontend_preview_action(menu_items, request, context)
    assert result is None
    assert menu_items == []  # Should not modify menu_items

    # Test with page but no pk (create view)
    menu_items = []
    context = {"page": FakePage(pk=None)}
    result = wagtail_hooks.add_frontend_preview_action(menu_items, request, context)
    assert result is None
    assert menu_items == []


def test_construct_page_action_menu_exception_handling(monkeypatch):
    """Test that exceptions during action menu construction are handled gracefully."""
    menu_items = []
    request = type("R", (), {"user": type("U", (), {"pk": 5})()})()
    context = {"page": FakePage(pk=1, slug="test")}

    # Patch reverse to raise an exception to test the except block
    def raise_error(*args, **kwargs):
        raise RuntimeError("reverse failed")

    monkeypatch.setattr(wagtail_hooks, "reverse", raise_error)

    # Should return None and not modify menu_items
    result = wagtail_hooks.add_frontend_preview_action(menu_items, request, context)
    assert result is None
    assert menu_items == []  # Should not modify due to exception


def test_construct_page_action_menu_insert_exception(monkeypatch):
    """Test that exceptions during menu_items.insert are handled gracefully."""
    # Mock menu_items that raises on insert
    class BadMenuItems(list):
        def insert(self, index, item):
            raise RuntimeError("insert failed")

    menu_items = BadMenuItems()
    request = type("R", (), {"user": type("U", (), {"pk": 5})()})()
    context = {"page": FakePage(pk=1, slug="test")}

    # Should return None and not break
    result = wagtail_hooks.add_frontend_preview_action(menu_items, request, context)
    assert result is None


def test_add_page_to_parent_raises_when_parent_is_none():
    """Test that _add_page_to_parent raises ValueError when parent_page is None."""
    # Since the function checks parent_page first, the page argument can be
    # any object; using a simple sentinel avoids unnecessary DB access.
    sentinel = object()

    with pytest.raises(ValueError, match="parent_page cannot be None"):
        _add_page_to_parent(page=sentinel, parent_page=None)
    sentinel = object()



