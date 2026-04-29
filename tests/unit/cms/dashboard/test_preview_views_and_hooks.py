import config
import datetime
import unittest.mock as mock
from urllib.parse import parse_qs, urlparse

import pytest

from common.virtual_clock import parse_embargo_time_value
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import JsonResponse
from django.urls import NoReverseMatch
from django.test import RequestFactory
from wagtail.admin.widgets import Button

from cms.dashboard import wagtail_hooks
from cms.dashboard.views import (
    InvalidPreviewFrontendUrlError,
    LinkBrowseView,
    MissingPreviewFrontendHostConfigurationError,
    PreviewToFrontendRedirectView,
)

MODULE_PATH = "cms"


class TestPreviewConfigurationErrors:
    def test_missing_preview_frontend_host_configuration_error_message(self):
        """
        Given missing preview frontend host configuration
        When the error is instantiated
        Then the configured guidance message is returned
        """
        error = MissingPreviewFrontendHostConfigurationError()

        assert str(error) == "FRONTEND_URL must define an absolute http(s) URL"

    def test_invalid_preview_frontend_url_error_message(self):
        """
        Given an invalid preview frontend URL
        When the error is instantiated
        Then the absolute-URL guidance message is returned
        """
        error = InvalidPreviewFrontendUrlError()

        assert (
            str(error) == "Preview redirects must use an absolute http(s) frontend URL"
        )


class TestEmbargoTime:
    @pytest.mark.parametrize(
        "embargo_time_value,expected_epoch",
        [(1711456200, 1711456200), (1711456200.9, 1711456200)],
    )
    def test_accepts_numeric_epoch_values(self, embargo_time_value, expected_epoch):
        """
        Given a numeric embargo time value
        When parse_embargo_time_value is called
        Then the corresponding UTC datetime is returned
        """
        actual = parse_embargo_time_value(embargo_time_value)

        assert actual == datetime.datetime.fromtimestamp(
            expected_epoch, tz=datetime.UTC
        )

    @pytest.mark.parametrize("embargo_time_value", [True, False, object()])
    def test_returns_none_for_unsupported_types(self, embargo_time_value):
        """
        Given an unsupported embargo time value type
        When parse_embargo_time_value is called
        Then None is returned
        """
        assert parse_embargo_time_value(embargo_time_value) is None

    @mock.patch("common.virtual_clock.datetime.datetime")
    def test_returns_none_when_timestamp_cannot_be_converted(
        self, spy_datetime_class: mock.MagicMock
    ):
        """
        Given an epoch value that cannot be converted to datetime
        When parse_embargo_time_value is called
        Then None is returned
        """
        spy_datetime_class.fromtimestamp.side_effect = OverflowError

        assert parse_embargo_time_value("1711456200") is None

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_passes_through_embargo_time_now(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given a preview request with embargo_time set to now
        When the preview redirect view is requested
        Then the redirect query includes et=now
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get(
            "/cms-admin/preview-to-frontend/1/",
            data={"embargo_time": "now"},
        )
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        parsed_query = parse_qs(urlparse(location).query)

        assert parsed_query["et"] == ["now"]

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_passes_through_embargo_time_epoch(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given a preview request with an epoch embargo_time value
        When the preview redirect view is requested
        Then the redirect query includes the same epoch value in et
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get(
            "/cms-admin/preview-to-frontend/1/",
            data={"embargo_time": "1711456200"},
        )
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        parsed_query = parse_qs(urlparse(location).query)

        assert parsed_query["et"] == ["1711456200"]

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_drops_blank_embargo_time(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given a preview request with blank embargo_time
        When the preview redirect view is requested
        Then the redirect query does not include et
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get(
            "/cms-admin/preview-to-frontend/1/",
            data={"embargo_time": "   "},
        )
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        parsed_query = parse_qs(urlparse(location).query)

        assert "et" not in parsed_query

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_drops_unparseable_embargo_time(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given a preview request with unparseable embargo_time
        When the preview redirect view is requested
        Then the redirect query does not include et
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get(
            "/cms-admin/preview-to-frontend/1/",
            data={"embargo_time": "not-a-time"},
        )
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        parsed_query = parse_qs(urlparse(location).query)

        assert "et" not in parsed_query


class TestAddFrontendPreviewActionExceptions:
    @mock.patch("cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView")
    @mock.patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch)
    def test_no_reverse_match_hides_preview_action(self, mock_reverse, mock_view):
        """
        Given reverse raises NoReverseMatch
        When add_frontend_preview_action is called
        Then no preview action is added
        """
        page = mock.MagicMock(
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
            PAGE_PREVIEWS_ENABLED=True,
        ):
            wagtail_hooks.add_frontend_preview_action(menu_items, None, {"page": page})
        assert menu_items == []


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
        """
        Given a page and a non-edit view name
        When frontend_preview_button is called
        Then no preview buttons are returned
        """
        page = FakePage()
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="index"
        )
        assert buttons == []

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.reverse")
    def test_no_reverse_match_hides_preview_button(
        self, spy_reverse: mock.MagicMock, settings
    ):
        """
        Given reverse raises NoReverseMatch and preview base URL is configured
        When frontend_preview_button is called for an editable preview-enabled page
        Then no Preview button is returned
        """
        spy_reverse.side_effect = NoReverseMatch("no reverse")
        page = mock.MagicMock(
            pk=123,
            slug="bar",
            custom_preview_enabled=True,
            has_unpublished_changes=True,
            live=False,
        )
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="edit"
        )
        assert buttons == []

    def test_live_non_draft_page_label_is_view_live(self):
        """
        Given a live page with no unpublished changes
        When frontend_preview_button is called
        Then the button label is View Live
        """
        page = mock.MagicMock(
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
        """
        Given a preview-enabled page that is neither draft nor live
        When frontend_preview_button is called
        Then no buttons are returned
        """
        page = mock.MagicMock(
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
        """
        Given a page type without custom preview support
        When frontend_preview_button is called
        Then no buttons are returned
        """
        page = FakePage(pk=123, slug="bar")
        buttons = wagtail_hooks.frontend_preview_button(
            page=page, user=None, next_url=None, view_name="edit"
        )
        assert buttons == []


class TestPreviewToFrontendRedirectView:
    def test_build_route_slug_uses_nested_page_path_when_available(self):
        """
        Given get_url_parts returns a nested page path
        When build_route_slug is called
        Then the nested path is converted into the route slug
        """
        page = mock.MagicMock(slug="covid-19")
        page.get_url_parts.return_value = (
            1,
            "https://frontend.test",
            "/respiratory-viruses/covid-19/",
        )
        route_slug = PreviewToFrontendRedirectView.build_route_slug(page=page)
        assert route_slug == "respiratory-viruses/covid-19"

    @pytest.mark.parametrize("page_path", [None, "", "/", "///"])
    def test_build_route_slug_falls_back_to_slug_when_path_is_empty(self, page_path):
        """
        Given get_url_parts returns an empty-like path
        When build_route_slug is called
        Then the page slug is used as the fallback route slug
        """
        page = mock.MagicMock(slug="fallback-slug")
        page.get_url_parts.return_value = (1, "https://frontend.test", page_path)

        route_slug = PreviewToFrontendRedirectView.build_route_slug(page=page)

        assert route_slug == "fallback-slug"

    @pytest.mark.parametrize("exception", [AttributeError(), TypeError(), ValueError()])
    def test_build_route_slug_falls_back_to_slug_on_expected_exceptions(
        self, exception
    ):
        """
        Given get_url_parts raises an expected exception
        When build_route_slug is called
        Then the page slug is used as the fallback route slug
        """
        page = mock.MagicMock(slug="fallback-slug")
        page.get_url_parts.side_effect = exception

        route_slug = PreviewToFrontendRedirectView.build_route_slug(page=page)

        assert route_slug == "fallback-slug"

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_permission_denied(self, spy_get_object_or_404: mock.MagicMock):
        """
        Given a user who cannot edit the page
        When the preview redirect view is requested
        Then PermissionDenied is raised
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="s", can_edit=False)

        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        with pytest.raises(PermissionDenied):
            view.get(request=request, pk=1)

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects(self, spy_get_object_or_404: mock.MagicMock, settings):
        """
        Given an editable page and a frontend preview base URL
        When the preview redirect view is requested
        Then the response redirects to the frontend preview URL with a token
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")

        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith("https://frontend.test/preview/cover?t=")

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_with_nested_route_slug(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given an editable page with a nested frontend path
        When the preview redirect view is requested
        Then the response uses the nested route slug in the redirect URL
        """
        page = FakePage(pk=1, slug="covid-19", can_edit=True)
        page.get_url_parts = lambda request=None: (
            1,
            "https://frontend.test",
            "/respiratory-viruses/covid-19/",
        )
        spy_get_object_or_404.return_value = page
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")

        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        assert location.startswith(
            "https://frontend.test/preview/respiratory-viruses/covid-19?t="
        )

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_success_redirects_appends_page_id_to_query(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given an editable page and a preview base URL
        When the preview redirect view is requested
        Then the redirect query includes slug, token, and page_id
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")

        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()
        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = "https://frontend.test"
        response = view.get(request=request, pk=1)
        location = (
            response.url if hasattr(response, "url") else response.get("Location")
        )
        parsed_query = parse_qs(urlparse(location).query)
        assert "t" in parsed_query
        assert parsed_query["page_id"] == ["1"]

    def test_validate_frontend_redirect_url_allows_configured_frontend_host(
        self, settings
    ):
        """
        Given a preview URL whose host matches the configured frontend allow-list
        When the redirect URL is validated
        Then the URL is accepted unchanged
        """
        config.FRONTEND_URL = "https://frontend.test"

        validated_url = PreviewToFrontendRedirectView.validate_frontend_redirect_url(
            frontend_url="https://frontend.test/preview?slug=cover&t=signed-token"
        )

        assert (
            validated_url == "https://frontend.test/preview?slug=cover&t=signed-token"
        )

    def test_validate_frontend_redirect_url_rejects_unconfigured_host(self, settings):
        """
        Given a preview URL whose host is outside the configured frontend allow-list
        When the redirect URL is validated
        Then an ImproperlyConfigured error is raised
        """
        config.FRONTEND_URL = "https://frontend.test"

        with pytest.raises(ImproperlyConfigured):
            PreviewToFrontendRedirectView.validate_frontend_redirect_url(
                frontend_url="https://malicious.test/preview?slug=cover&t=signed-token"
            )

    def test_validate_frontend_redirect_url_rejects_non_absolute_url(self, settings):
        """
        Given a relative preview redirect URL
        When the redirect URL is validated
        Then an ImproperlyConfigured error is raised
        """
        config.FRONTEND_URL = "https://frontend.test"

        with pytest.raises(ImproperlyConfigured):
            PreviewToFrontendRedirectView.validate_frontend_redirect_url(
                frontend_url="/preview?slug=cover&t=signed-token"
            )

    def test_validate_frontend_redirect_url_rejects_when_allow_list_is_empty(
        self, settings
    ):
        """
        Given frontend settings that do not define absolute http(s) hosts
        When the redirect URL is validated
        Then an ImproperlyConfigured error is raised
        """
        config.FRONTEND_URL = ""
        with pytest.raises(ImproperlyConfigured):
            PreviewToFrontendRedirectView.validate_frontend_redirect_url(
                frontend_url="https://frontend.test/preview?slug=cover&t=signed-token"
            )

    def test_build_frontend_route_url_includes_route_slug_and_validates_host(
        self, settings
    ):
        """
        Given a valid frontend base URL and non-empty route slug
        When build_frontend_route_url is called
        Then it returns the validated route URL with /nocache appended
        """
        config.FRONTEND_URL = "https://frontend.test"

        route_url = PreviewToFrontendRedirectView.build_frontend_route_url(
            base_url="https://frontend.test",
            route_slug="respiratory-viruses/covid-19",
        )

        assert route_url == "https://frontend.test/nocache/respiratory-viruses/covid-19"

    def test_build_frontend_route_url_returns_base_root_when_slug_is_empty(
        self, settings
    ):
        """
        Given a valid frontend base URL and empty route slug
        When build_frontend_route_url is called
        Then it returns the validated frontend root URL with /nocache appended
        """
        config.FRONTEND_URL = "https://frontend.test"

        route_url = PreviewToFrontendRedirectView.build_frontend_route_url(
            base_url="https://frontend.test",
            route_slug="",
        )

        assert route_url == "https://frontend.test/nocache"

    def test_build_frontend_preview_base_url_appends_preview_path(self, settings):
        """
        Given a valid frontend base URL
        When build_frontend_preview_base_url is called
        Then it returns the validated frontend preview endpoint URL
        """
        config.FRONTEND_URL = "https://frontend.test"

        preview_url = PreviewToFrontendRedirectView.build_frontend_preview_base_url(
            base_url="https://frontend.test"
        )

        assert preview_url == "https://frontend.test/preview"

    @mock.patch(f"{MODULE_PATH}.dashboard.views.get_object_or_404")
    def test_redirect_raises_when_base_url_is_not_absolute(
        self, spy_get_object_or_404: mock.MagicMock, settings
    ):
        """
        Given a preview base URL that is not an absolute http(s) URL
        When the preview redirect view is requested
        Then an ImproperlyConfigured error is raised instead of redirecting
        """
        spy_get_object_or_404.return_value = FakePage(pk=1, slug="cover", can_edit=True)
        request = RequestFactory().get("/cms-admin/preview-to-frontend/1/")
        request.user = type("U", (), {"is_authenticated": True, "pk": 5})()

        view = PreviewToFrontendRedirectView()
        config.FRONTEND_URL = ""

        with pytest.raises(ImproperlyConfigured):
            view.get(request=request, pk=1)


class TestAddFrontendPreviewAction:
    def test_missing_page_or_pk_returns_none(self):
        """
        Given missing page context or an unsaved page without pk
        When add_frontend_preview_action is called
        Then menu items remain unchanged
        """
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
        request = mock.MagicMock()
        request.user = mock.MagicMock(pk=5)
        context = {"page": FakePage(pk=1, slug="test")}

        # When
        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=request,
            context=context,
        )


class TestLinkBrowseView:
    def test_intercept_request_switches_off_email_and_phone_links(self):
        """
        Given chooser request query params
        When LinkBrowseView intercepts the request
        Then email and phone link flags are forced off
        """
        request = RequestFactory().get(
            "/cms-admin/choose-link/",
            data={"allow_email_link": "true", "allow_phone_link": "true"},
        )

        intercepted_request = (
            LinkBrowseView._intercept_request_and_switch_off_extra_links(
                request=request
            )
        )

        assert intercepted_request.GET["allow_email_link"] is False
        assert intercepted_request.GET["allow_phone_link"] is False

    @mock.patch(f"{MODULE_PATH}.dashboard.views.BrowseView.get")
    @mock.patch.object(
        LinkBrowseView,
        "_intercept_request_and_switch_off_extra_links",
    )
    def test_get_intercepts_then_delegates_to_super(
        self,
        spy_intercept_request_and_switch_off_extra_links: mock.MagicMock,
        spy_browse_view_get: mock.MagicMock,
    ):
        """
        Given a chooser browse request
        When LinkBrowseView.get is called
        Then request interception runs before delegating to the parent view
        """
        request = RequestFactory().get("/cms-admin/choose-link/")
        intercepted_request = RequestFactory().get("/cms-admin/choose-link/")
        spy_intercept_request_and_switch_off_extra_links.return_value = (
            intercepted_request
        )
        expected_response = JsonResponse({"ok": True})
        spy_browse_view_get.return_value = expected_response

        response = LinkBrowseView().get(request=request, parent_page_id=17)

        spy_intercept_request_and_switch_off_extra_links.assert_called_once_with(
            request=request
        )
        spy_browse_view_get.assert_called_once_with(
            request=intercepted_request, parent_page_id=17
        )
        assert response is expected_response

    @mock.patch(f"{MODULE_PATH}.dashboard.wagtail_hooks.logger.debug")
    @mock.patch(
        f"{MODULE_PATH}.dashboard.wagtail_hooks._get_preview_button_label",
        side_effect=RuntimeError("boom"),
    )
    def test_internal_errors_are_logged_and_ignored(
        self,
        spy_get_preview_button_label: mock.MagicMock,
        spy_logger_exception: mock.MagicMock,
    ):
        """
        Given add_frontend_preview_action encounters an unexpected internal error
        When the action is being constructed
        Then the error is logged and the menu remains unchanged
        """
        page = mock.MagicMock(pk=1, slug="preview-target")
        menu_items = []

        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=None,
            context={"page": page},
        )

        assert menu_items == []
        spy_get_preview_button_label.assert_called_once_with(page=page)
        spy_logger_exception.assert_called_once_with(
            "Failed to construct frontend preview action; editor UI will continue"
        )

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
        page = mock.MagicMock(
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
