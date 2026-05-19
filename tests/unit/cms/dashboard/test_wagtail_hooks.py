import pytest
import config
from unittest import mock
from unittest.mock import patch
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch
from draftjs_exporter.dom import DOM
from wagtail.admin.site_summary import SummaryItem
from wagtail.models import Page
from cms.dashboard import wagtail_hooks
from cms.dashboard.wagtail_hooks import (
    _build_link_props,
    link_entity_with_href,
)
from django.test import override_settings


class TestWagtailHooksPagePreviews:
    @patch("cms.dashboard.wagtail_hooks._rewrite_post_publish_view_live_button_url")
    def test_after_edit_hook_calls_rewrite_helper(self, mock_rewrite):
        """
        Given a request and page
        When rewrite_post_publish_view_live_button_after_edit is called
        Then it delegates to _rewrite_post_publish_view_live_button_url
        """
        request = mock.Mock()
        page = mock.Mock()

        wagtail_hooks.rewrite_post_publish_view_live_button_after_edit(
            request=request,
            page=page,
        )

        mock_rewrite.assert_called_once_with(request=request, page=page)

    @patch("cms.dashboard.wagtail_hooks._rewrite_post_publish_view_live_button_url")
    def test_after_create_hook_calls_rewrite_helper(self, mock_rewrite):
        """
        Given a request and page
        When rewrite_post_publish_view_live_button_after_create is called
        Then it delegates to _rewrite_post_publish_view_live_button_url
        """
        request = mock.Mock()
        page = mock.Mock()

        wagtail_hooks.rewrite_post_publish_view_live_button_after_create(
            request=request,
            page=page,
        )

        mock_rewrite.assert_called_once_with(request=request, page=page)

    @patch("cms.dashboard.wagtail_hooks._build_view_live_url")
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=False)
    def test_rewrite_post_publish_view_live_button_url_returns_when_previews_disabled(
        self,
        _mock_settings,
        mock_build_view_live_url,
    ):
        """
        Given page previews are disabled
        When _rewrite_post_publish_view_live_button_url is called
        Then live URL building is skipped
        """
        request = mock.Mock()
        page = mock.Mock(live=True)

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request, page=page
        )

        mock_build_view_live_url.assert_not_called()

    @patch("cms.dashboard.wagtail_hooks._build_view_live_url")
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_rewrite_post_publish_view_live_button_url_returns_when_page_not_live(
        self,
        _mock_settings,
        mock_build_view_live_url,
    ):
        """
        Given previews are enabled but the page is not live
        When _rewrite_post_publish_view_live_button_url is called
        Then live URL building is skipped
        """
        request = mock.Mock()
        page = mock.Mock(live=False)

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request, page=page
        )

        mock_build_view_live_url.assert_not_called()

    @patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None)
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_rewrite_post_publish_view_live_button_url_returns_when_no_live_url(
        self,
        _mock_settings,
        mock_build_view_live_url,
    ):
        """
        Given previews are enabled and the page is live
        When _build_view_live_url returns no URL
        Then the rewrite flow exits after attempting to build the live URL
        """
        request = mock.Mock()
        page = mock.Mock(live=True)

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request, page=page
        )

        mock_build_view_live_url.assert_called_once_with(page=page)

    @patch(
        "cms.dashboard.wagtail_hooks._build_view_live_url",
        return_value="http://localhost:3000/x/",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_rewrite_post_publish_view_live_button_url_returns_when_no_message_storage(
        self,
        _mock_settings,
        _mock_build_view_live_url,
    ):
        """
        Given previews are enabled and request has no message storage
        When _rewrite_post_publish_view_live_button_url is called
        Then it exits without raising errors
        """
        request = mock.Mock(spec=[])
        page = mock.Mock(live=True)

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request, page=page
        )

    @patch(
        "cms.dashboard.wagtail_hooks._build_view_live_url",
        return_value="http://localhost:3000/x/",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_rewrite_post_publish_view_live_button_url_continues_when_messages_list_empty(
        self,
        _mock_settings,
        _mock_build_view_live_url,
    ):
        """
        Given previews are enabled and message storage contains no messages
        When _rewrite_post_publish_view_live_button_url is called
        Then it exits without modifying anything
        """
        request = mock.Mock()
        request._messages = mock.Mock(_queued_messages=[], _loaded_messages=[])
        page = mock.Mock(live=True)

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request, page=page
        )

    @patch(
        "cms.dashboard.wagtail_hooks._build_view_live_url",
        return_value="http://localhost:3000/x/",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_rewrite_post_publish_view_live_button_url_continues_when_no_view_live_text(
        self,
        _mock_settings,
        _mock_build_view_live_url,
    ):
        """
        Given previews are enabled and message text has no View live anchor
        When _rewrite_post_publish_view_live_button_url is called
        Then the original message text is left unchanged
        """
        request = mock.Mock()
        message = mock.Mock()
        message.message = "Page has been published"
        request._messages = mock.Mock(_queued_messages=[message], _loaded_messages=[])
        page = mock.Mock(live=True)

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request, page=page
        )

        assert message.message == "Page has been published"

    @patch("cms.dashboard.wagtail_hooks.logger.debug")
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label",
        side_effect=RuntimeError("boom"),
    )
    def test_add_frontend_preview_action_logs_and_swallows_unexpected_error(
        self,
        _mock_label,
        _mock_settings,
        spy_logger_exception,
    ):
        """
        Given add_frontend_preview_action encounters an unexpected runtime error
        When the function is invoked
        Then the exception is logged and not re-raised
        """
        page = mock.Mock()
        page.pk = 123
        menu_items = []
        context = {"page": page}

        wagtail_hooks.add_frontend_preview_action(
            menu_items=menu_items,
            request=None,
            context=context,
        )

        spy_logger_exception.assert_called_once()

    @patch("cms.dashboard.wagtail_hooks.logger.exception")
    @patch(
        "cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_frontend_route_url",
        side_effect=ImproperlyConfigured,
    )
    def test_build_view_live_url_invalid_base_returns_none(
        self, _mock_route_url, spy_logger_exception
    ):
        """
        Given FRONTEND_URL is missing or non-absolute
        When _build_view_live_url is called
        Then None is returned to avoid generating a relative URL
        """
        page = mock.Mock()
        page.slug = "access-our-data"
        assert wagtail_hooks._build_view_live_url(page) is None

        spy_logger_exception.assert_called_once()

    @patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/888")
    def test__build_frontend_preview_url(self, mock_reverse):
        """
        Given a page,
        When _build_frontend_preview_url is called,
        Then it returns the preview URL from reverse.
        """
        page = mock.Mock()
        page.pk = 888
        url = wagtail_hooks._build_frontend_preview_url(page=page)
        assert url == "/admin/preview/888"
        """
        Given label 'View Live' and live_url is falsy,
        When frontend_preview_button is called and reverse raises NoReverseMatch,
        Then it returns no buttons.
        """
        page = mock.Mock()
        page.pk = 123
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings",
            PAGE_PREVIEWS_ENABLED=True,
        ):
            with mock.patch(
                "cms.dashboard.wagtail_hooks._get_preview_button_label",
                return_value="View Live",
            ):
                with mock.patch(
                    "cms.dashboard.wagtail_hooks._build_view_live_url",
                    return_value=None,
                ):
                    with mock.patch(
                        "cms.dashboard.wagtail_hooks.reverse",
                        side_effect=NoReverseMatch(),
                    ):
                        with mock.patch(
                            "cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug",
                            return_value="sluggy",
                        ):
                            with mock.patch(
                                "cms.dashboard.wagtail_hooks.Button",
                                side_effect=lambda **kwargs: type("Btn", (), kwargs)(),
                            ):
                                result = wagtail_hooks.frontend_preview_button(
                                    page, user=None, next_url=None, view_name="edit"
                                )
                                assert result == []

    @patch(
        "cms.dashboard.wagtail_hooks.FrontendPreviewAction",
        side_effect=lambda **kwargs: type("FPA", (), kwargs)(),
    )
    @patch(
        "cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug",
        return_value="sluggy",
    )
    @patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch())
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"
    )
    @patch(
        "cms.dashboard.wagtail_hooks.settings",
        PAGE_PREVIEWS_ENABLED=True,
    )
    def test_add_frontend_preview_action_preview_branch_no_reverse_match(
        self, mock_settings, mock_label, mock_reverse, mock_slug, mock_fpa
    ):
        """
        Given label 'Preview' and reverse raises NoReverseMatch,
        When add_frontend_preview_action is called,
        Then no preview action is inserted.
        """
        page = mock.Mock()
        page.pk = 456
        menu_items = []
        context = {"page": page}
        wagtail_hooks.add_frontend_preview_action(
            menu_items, request=None, context=context
        )
        assert menu_items == []

    @patch(
        "cms.dashboard.wagtail_hooks.Button",
        side_effect=lambda **kwargs: type("Btn", (), kwargs)(),
    )
    @patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/42")
    @patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None)
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label",
        return_value="View Live",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_frontend_preview_button_view_live_fallback_preview(
        self, mock_settings, mock_label, mock_build_url, mock_reverse, mock_button
    ):
        """
        Given label 'View Live' and live_url is falsy,
        When frontend_preview_button is called and reverse succeeds,
        Then it returns a Button with the preview URL from reverse.
        """
        page = mock.Mock()
        page.pk = 42
        result = wagtail_hooks.frontend_preview_button(
            page, user=None, next_url=None, view_name="edit"
        )
        assert len(result) == 1
        assert getattr(result[0], "url", None) == "/admin/preview/42"

    @patch(
        "cms.dashboard.wagtail_hooks.Button",
        side_effect=lambda **kwargs: type("Btn", (), kwargs)(),
    )
    @patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/42")
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label",
        return_value="View Live",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_frontend_preview_button_view_live_invalid_base_uses_preview_url(
        self, mock_settings, mock_label, mock_reverse, mock_button
    ):
        """
        Given label 'View Live' but FRONTEND_URL is invalid
        When frontend_preview_button is called
        Then it falls back to the preview redirect URL
        """
        page = mock.Mock()
        page.pk = 42
        page.slug = "access-our-data"
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings",
            PAGE_PREVIEWS_ENABLED=True,
            FRONTEND_URL="",
        ):
            result = wagtail_hooks.frontend_preview_button(
                page, user=None, next_url=None, view_name="edit"
            )
        assert len(result) == 1
        assert getattr(result[0], "url", None) == "/admin/preview/42"

    @patch(
        "cms.dashboard.wagtail_hooks.FrontendPreviewAction",
        side_effect=lambda **kwargs: type("FPA", (), kwargs)(),
    )
    @patch("cms.dashboard.wagtail_hooks.reverse", return_value="/admin/preview/99")
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_add_frontend_preview_action_preview_branch(
        self, mock_settings, mock_label, mock_reverse, mock_fpa
    ):
        """
        Given label 'Preview' and reverse succeeds,
        When add_frontend_preview_action is called,
        Then it inserts a FrontendPreviewAction with the preview URL from reverse.
        """
        page = mock.Mock()
        page.pk = 99
        menu_items = []
        context = {"page": page}
        wagtail_hooks.add_frontend_preview_action(
            menu_items, request=None, context=context
        )
        assert len(menu_items) == 1
        assert getattr(menu_items[0], "url", None) == "/admin/preview/99"

    @patch(
        "cms.dashboard.wagtail_hooks.FrontendPreviewAction",
        side_effect=lambda **kwargs: type("FPA", (), kwargs)(),
    )
    @patch(
        "cms.dashboard.wagtail_hooks.reverse",
        side_effect=["/admin/preview/77", "/admin/preview/99"],
    )
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_add_frontend_preview_action_preview_branch_explicit(
        self, mock_settings, mock_label, mock_reverse, mock_fpa
    ):
        """
        Given label 'Preview' and reverse succeeds,
        When add_frontend_preview_action is called,
        Then it inserts a FrontendPreviewAction with the preview URL from reverse (explicit branch coverage).
        """
        page = mock.Mock()
        page.pk = 77
        menu_items = []
        context = {"page": page}
        wagtail_hooks.add_frontend_preview_action(
            menu_items, request=None, context=context
        )
        assert len(menu_items) == 1
        assert getattr(menu_items[0], "url", None) == "/admin/preview/77"
        # Reset menu_items before the next call to avoid accumulation
        menu_items = []
        wagtail_hooks.add_frontend_preview_action(
            menu_items, request=None, context=context
        )
        assert len(menu_items) == 1
        assert getattr(menu_items[0], "url", None) == "/admin/preview/99"

    @patch("cms.dashboard.wagtail_hooks._build_frontend_preview_url")
    @patch(
        "cms.dashboard.wagtail_hooks.FrontendPreviewAction",
        side_effect=lambda **kwargs: type("FPA", (), kwargs)(),
    )
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label", return_value="Preview"
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_add_frontend_preview_action_calls_url_builder_for_preview_label(
        self, mock_settings, mock_label, mock_fpa, mock_build_url
    ):
        """
        Given Preview is the selected button label
        When add_frontend_preview_action is called
        Then the frontend preview URL builder is used to create the action URL
        """
        page = mock.Mock()
        page.pk = 123
        menu_items = []
        context = {"page": page}
        mock_build_url.return_value = "/admin/preview/123"

        wagtail_hooks.add_frontend_preview_action(
            menu_items, request=None, context=context
        )

        mock_build_url.assert_called_once_with(page=page)
        assert len(menu_items) == 1
        assert getattr(menu_items[0], "url", None) == "/admin/preview/123"

    @patch(
        "cms.dashboard.wagtail_hooks.Button",
        side_effect=lambda **kwargs: type("Btn", (), kwargs)(),
    )
    @patch(
        "cms.dashboard.wagtail_hooks._build_view_live_url", return_value="https://live"
    )
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label",
        return_value="View Live",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_frontend_preview_button_view_live_truthy_url(
        self, mock_settings, mock_label, mock_build_url, mock_button
    ):
        """
        Given label 'View Live' and live_url is truthy,
        When frontend_preview_button is called,
        Then it returns a Button with the live_url.
        """
        page = mock.Mock()
        result = wagtail_hooks.frontend_preview_button(
            page, user=None, next_url=None, view_name="edit"
        )
        assert len(result) == 1
        assert getattr(result[0], "url", None) == "https://live"

    def test_frontend_preview_button_view_name_not_edit(self):
        """
        Given view_name is not 'edit',
        When frontend_preview_button is called,
        Then it returns [].
        """
        page = mock.Mock()
        result = wagtail_hooks.frontend_preview_button(
            page, user=None, next_url=None, view_name="not-edit"
        )
        assert result == []

    def test_frontend_preview_button_previews_disabled(self):
        """
        Given PAGE_PREVIEWS_ENABLED is False,
        When frontend_preview_button is called,
        Then it returns [].
        """
        page = mock.Mock()
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=False
        ):
            result = wagtail_hooks.frontend_preview_button(
                page, user=None, next_url=None, view_name="edit"
            )
            assert result == []

    def test_get_preview_button_label_custom_preview_disabled(self):
        """
        Given a page with custom_preview_enabled False,
        When _get_preview_button_label is called,
        Then it returns None.
        """
        page = mock.Mock()
        page.custom_preview_enabled = False
        assert wagtail_hooks._get_preview_button_label(page) is None

    @patch(
        "cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug",
        return_value="sluggy",
    )
    @patch(
        "cms.dashboard.wagtail_hooks.settings",
    )
    @patch("cms.dashboard.wagtail_hooks.reverse", side_effect=NoReverseMatch())
    @patch("cms.dashboard.wagtail_hooks._build_view_live_url", return_value=None)
    @patch(
        "cms.dashboard.wagtail_hooks._get_preview_button_label",
        return_value="View Live",
    )
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_frontend_preview_button_view_live_falsy_url(
        self,
        mock_enabled,
        mock_label,
        mock_build_url,
        mock_reverse,
        mock_tpl,
        mock_slug,
    ):
        """
        Given label 'View Live' and live_url is falsy,
        When frontend_preview_button is called,
        Then no preview button is returned.
        """
        page = mock.Mock()
        result = wagtail_hooks.frontend_preview_button(
            page, user=None, next_url=None, view_name="edit"
        )
        assert result == []

    def test_add_frontend_preview_action_view_live_falsy_url(self):
        """
        Given label 'View Live' and live_url is falsy,
        When add_frontend_preview_action is called,
        Then it returns early (None).
        """
        page = mock.Mock()
        page.pk = 1
        menu_items = []
        context = {"page": page}
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True
        ):
            with mock.patch(
                "cms.dashboard.wagtail_hooks._get_preview_button_label",
                return_value="View Live",
            ):
                with mock.patch(
                    "cms.dashboard.wagtail_hooks._build_view_live_url",
                    return_value=None,
                ):
                    wagtail_hooks.add_frontend_preview_action(menu_items, None, context)

    def test_get_preview_button_label_preview(self):
        """
        Given a page with draft,
        When _get_preview_button_label is called,
        Then it returns 'Preview'.
        """
        page = mock.Mock()
        page.custom_preview_enabled = True
        page.has_unpublished_changes = True
        page.live = False
        assert wagtail_hooks._get_preview_button_label(page) == "Preview"

    def test_get_preview_button_label_view_live(self):
        """
        Given a page with live,
        When _get_preview_button_label is called,
        Then it returns 'View Live'.
        """
        page = mock.Mock()
        page.custom_preview_enabled = True
        page.has_unpublished_changes = False
        page.live = True
        assert wagtail_hooks._get_preview_button_label(page) == "View Live"

    def test_get_preview_button_label_none(self):
        """
        Given a page with neither draft nor live,
        When _get_preview_button_label is called,
        Then it returns None.
        """
        page = mock.Mock()
        page.custom_preview_enabled = True
        page.has_unpublished_changes = False
        page.live = False
        assert wagtail_hooks._get_preview_button_label(page) is None

    def test_build_view_live_url_exception_and_slug(self):
        """
        Given a page where get_url_parts raises AttributeError,
        When _build_view_live_url is called,
        Then it returns slug url or None.
        """
        config.FRONTEND_URL = "http://localhost:3000"
        page = mock.Mock()
        page.get_url_parts.side_effect = AttributeError()
        page.slug = "sluggy"
        build_view_live_url = wagtail_hooks._build_view_live_url(page)
        assert build_view_live_url == "http://localhost:3000/nocache/sluggy"
        page.slug = ""
        build_view_live_url = wagtail_hooks._build_view_live_url(page)
        assert build_view_live_url == "http://localhost:3000/nocache"

    def test_build_view_live_url_success(self):
        """
        Given a page where get_url_parts returns a path,
        When _build_view_live_url is called,
        Then it returns the correct live URL using the path.
        """
        config.FRONTEND_URL = "http://localhost:3000"
        page = mock.Mock()
        page.get_url_parts.return_value = ("http", "domain", "/foo/bar/")
        view_live_url = wagtail_hooks._build_view_live_url(page)
        assert view_live_url == "http://localhost:3000/nocache/foo/bar"

    def test_frontend_preview_button_label_none(self):
        """
        Given _get_preview_button_label returns None,
        When frontend_preview_button is called,
        Then it returns [].
        """
        page = mock.Mock()
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True
        ):
            with mock.patch(
                "cms.dashboard.wagtail_hooks._get_preview_button_label",
                return_value=None,
            ):
                result = wagtail_hooks.frontend_preview_button(
                    page, user=None, next_url=None, view_name="edit"
                )
                assert result == []

    def test_frontend_preview_button_view_live_no_url(self):
        """
        Given label 'View Live' but no live_url,
        When frontend_preview_button is called and reverse fails,
        Then no button is returned.
        """
        page = mock.Mock()
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True
        ):
            with mock.patch(
                "cms.dashboard.wagtail_hooks._get_preview_button_label",
                return_value="View Live",
            ):
                with mock.patch(
                    "cms.dashboard.wagtail_hooks._build_view_live_url",
                    return_value=None,
                ):
                    with mock.patch(
                        "cms.dashboard.wagtail_hooks.reverse",
                        side_effect=NoReverseMatch(),
                    ):
                        with mock.patch(
                            "cms.dashboard.wagtail_hooks.settings",
                            FRONTEND_URL="https://frontend.test",
                        ):
                            with mock.patch(
                                "cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug",
                                return_value="sluggy",
                            ):
                                result = wagtail_hooks.frontend_preview_button(
                                    page, user=None, next_url=None, view_name="edit"
                                )
                                assert result == []

    def test_register_admin_urls(self):
        """
        Given nothing,
        When register_admin_urls is called,
        Then it returns a list with a re_path.
        """
        result = wagtail_hooks.register_admin_urls()
        assert isinstance(result, list)
        assert result

    def test_add_frontend_preview_action_early_returns(self):
        """
        Given missing or invalid page/context/settings,
        When add_frontend_preview_action is called,
        Then it returns early (None).
        """
        # No page
        menu_items = []
        context = {}
        wagtail_hooks.add_frontend_preview_action(menu_items, None, context)
        # No pk
        page = mock.Mock()
        page.pk = None
        context = {"page": page}
        wagtail_hooks.add_frontend_preview_action(menu_items, None, context)
        # PAGE_PREVIEWS_ENABLED False
        page.pk = 1
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=False
        ):
            wagtail_hooks.add_frontend_preview_action(menu_items, None, {"page": page})
        # button_label None
        with mock.patch(
            "cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True
        ):
            with mock.patch(
                "cms.dashboard.wagtail_hooks._get_preview_button_label",
                return_value=None,
            ):
                wagtail_hooks.add_frontend_preview_action(
                    menu_items, None, {"page": page}
                )

    def test_replace_view_live_button_href_rewrites_only_view_live_anchor(self):
        """
        Given a publish success message containing a View live anchor
        When _replace_view_live_button_href is called with a frontend target URL
        Then only the anchor href is rewritten and safe link attributes are added
        """
        message_html = (
            '<span>ok</span><a href="http://localhost:8000/foo/" '
            'class="button button-small button-secondary">View live</a>'
        )

        result = wagtail_hooks._replace_view_live_button_href(
            message_html=message_html,
            target_url="http://localhost:3000/foo/",
        )

        assert 'href="http://localhost:3000/foo/"' in result
        assert 'target="_blank"' in result
        assert 'rel="noreferrer"' in result

    @patch("cms.dashboard.wagtail_hooks._build_view_live_url")
    @patch("cms.dashboard.wagtail_hooks.settings", PAGE_PREVIEWS_ENABLED=True)
    def test_rewrite_post_publish_view_live_button_url_updates_message(
        self,
        _mock_settings,
        mock_build_view_live_url,
    ):
        """
        Given previews are enabled and a queued publish message contains View live
        When _rewrite_post_publish_view_live_button_url is called
        Then the backend live link is replaced with the frontend live link
        """
        mock_build_view_live_url.return_value = (
            "http://localhost:3000/weather-health-alerts/"
        )

        request = mock.Mock()
        message = mock.Mock()
        message.message = (
            '<a href="http://localhost:8000/weather-health-alerts/" '
            'class="button button-small button-secondary">View live</a>'
        )
        request._messages = mock.Mock(_queued_messages=[message], _loaded_messages=[])

        page = mock.Mock()
        page.live = True

        wagtail_hooks._rewrite_post_publish_view_live_button_url(
            request=request,
            page=page,
        )

        assert "http://localhost:3000/weather-health-alerts/" in message.message
        assert "http://localhost:8000/weather-health-alerts/" not in message.message
        assert 'target="_blank"' in message.message
        assert 'rel="noreferrer"' in message.message


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
        expected_value = f'<link rel="stylesheet" type="text/css" href="{returned_static_css_theme}">'
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


@pytest.fixture(autouse=True)
def disable_wagtail_hooks():
    """
    Replace wagtail.hooks.register with a no-op decorator so
    functions behave like normal Python functions in tests.
    """
    with patch("wagtail.hooks.register", lambda *a, **k: (lambda f: f)):
        yield


class TestAddFrontendPreviewActionBranches:
    @pytest.mark.parametrize(
        "pk,reverse_side_effect,slug,expected_url",
        [
            # reverse raises NoReverseMatch
            (
                456,
                NoReverseMatch(),
                "sluggy",
                "https://frontend.test/preview?slug=sluggy",
            ),
            # reverse returns preview url
            (99, "/admin/preview/99", None, "/admin/preview/99"),
            # explicit branch coverage, two calls
            (77, "/admin/preview/77", None, "/admin/preview/77"),
            (99, "/admin/preview/99", None, "/admin/preview/99"),
        ],
    )
    def test_add_frontend_preview_action_branches(
        self, pk, reverse_side_effect, slug, expected_url
    ):
        """
        Given a page preview scenario with reverse outcomes
        When add_frontend_preview_action is called
        Then the inserted action URL matches the expected branch outcome
        """
        page = mock.Mock()
        page.pk = pk
        menu_items = []
        context = {"page": page}
        settings_patch = {
            "PAGE_PREVIEWS_ENABLED": True,
        }
        with mock.patch("cms.dashboard.wagtail_hooks.settings", **settings_patch):
            with mock.patch(
                "cms.dashboard.wagtail_hooks._get_preview_button_label",
                return_value="Preview",
            ):
                with mock.patch(
                    "cms.dashboard.wagtail_hooks.reverse",
                    side_effect=reverse_side_effect,
                ):
                    build_route_slug_patch = (
                        mock.patch(
                            "cms.dashboard.wagtail_hooks.PreviewToFrontendRedirectView.build_route_slug",
                            return_value=slug,
                        )
                        if slug
                        else mock.patch("builtins.id", lambda x: x)
                    )
                    with build_route_slug_patch:

                        def fpa_mock(**kwargs):
                            obj = type("FPA", (), {})()
                            obj._url = kwargs.get("url")
                            obj.label = kwargs.get("label")
                            obj.order = kwargs.get("order")
                            return obj

                        with mock.patch(
                            "cms.dashboard.wagtail_hooks.FrontendPreviewAction",
                            side_effect=fpa_mock,
                        ):
                            with mock.patch(
                                "cms.dashboard.wagtail_hooks._build_frontend_preview_url",
                                return_value=expected_url,
                            ):
                                wagtail_hooks.add_frontend_preview_action(
                                    menu_items, request=None, context=context
                                )
                                assert len(menu_items) == 1
                                actual_url = getattr(menu_items[0], "_url", None)
                                # Debug output removed after test confirmation
                                assert actual_url == expected_url


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


class TestFrontendPreviewAction:
    def test_get_url_returns_url(self):
        """
        Given a FrontendPreviewAction instance with a URL,
        When get_url is called,
        Then it returns the correct URL.
        """
        action = wagtail_hooks.FrontendPreviewAction(
            url="/test-url/", label="Test", order=1
        )
        assert action.get_url(parent_context=None) == "/test-url/"
