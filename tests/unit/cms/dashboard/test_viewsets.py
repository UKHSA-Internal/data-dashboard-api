from unittest import mock

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet

from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.dashboard.viewsets import CMSDraftPagesViewSet, CMSPagesAPIViewSet

MODULE_PATH = "cms.dashboard.viewsets"


class TestCMSDraftPagesViewSet:
    def test_base_serializer_class_is_set_with_correct_serializer(self):
        """
        Given an instance of the `CMSDraftPagesViewSet`
        When the `base_serializer_class` attribute is called
        Then the `CMSDraftPagesSerializer` class is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        base_serializer_class = draft_pages_viewset.base_serializer_class

        # Then
        assert base_serializer_class is CMSDraftPagesSerializer

    def test_get_urlpatterns(self):
        """
        Given an instance of the `CMSDraftPagesViewSet`
        When `get_urlpatterns()` is called
        Then only 1 detail-type url pattern is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        urlpatterns = draft_pages_viewset.get_urlpatterns()

        # Then
        assert len(urlpatterns) == 1
        assert urlpatterns[0].name == "detail"

    def test_permission_classes_has_no_api_key_constraint(self):
        """
        Given an instance of the `CMSDraftPagesViewSet`
        When `permission_classes` is called
        Then an empty list is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        permission_classes = draft_pages_viewset.permission_classes

        # Then
        assert permission_classes == []

    @mock.patch("cms.dashboard.viewsets.Page")
    def test_get_queryset_returns_all_specific_pages(
        self,
        spy_page_model: mock.MagicMock,
    ):
        """
        Given the draft pages viewset
        When get_queryset() is called
        Then it returns Page.objects.all().specific()

        Patches:
            `spy_page_model`: To control Page manager chain and assert calls.
        """
        # Given
        expected_queryset = object()
        spy_page_model.objects.all.return_value.specific.return_value = (
            expected_queryset
        )
        viewset = CMSDraftPagesViewSet()

        # When
        queryset = viewset.get_queryset()

        # Then
        assert queryset is expected_queryset
        spy_page_model.objects.all.assert_called_once_with()
        spy_page_model.objects.all.return_value.specific.assert_called_once_with()

    def test_normalise_route_slug_handles_none_value(self):
        """
        Given a None slug value
        When route slug normalization is applied
        Then an empty route slug is returned
        """
        # When
        route_slug = CMSDraftPagesViewSet._normalise_route_slug(slug=None)

        # Then
        assert route_slug == ""

    def test_detail_view_returns_401_without_valid_bearer_authorization(self):
        """
        Given a request with no bearer authorization header
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned
        """
        # Given
        request = RequestFactory().get("/api/drafts/test-page/")

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_401_for_non_bearer_authorization_scheme(self):
        """
        Given a request with an Authorization header that is not Bearer
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned
        """
        # Given
        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Token token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mock.patch(f"{MODULE_PATH}.loads")
    def test_detail_view_returns_401_when_token_cannot_be_loaded(
        self, spy_loads: mock.MagicMock
    ):
        """
        Given a request with a bearer token that cannot be decoded
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned

        Patches:
            `spy_loads`: To force token loading failure.
        """
        # Given
        spy_loads.side_effect = ValueError("bad token")
        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mock.patch.object(CMSDraftPagesViewSet, "_get_page_for_route_slug")
    @mock.patch(f"{MODULE_PATH}.loads")
    def test_detail_view_returns_401_when_page_id_does_not_match(
        self,
        spy_loads: mock.MagicMock,
        spy_get_page_for_route_slug: mock.MagicMock,
    ):
        """
        Given a token payload whose `page_id` does not match the request id
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned

        Patches:
            `spy_loads`: To return a payload with mismatched `page_id`.
        """
        # Given
        spy_get_page_for_route_slug.return_value = mock.Mock(pk=1)
        spy_loads.return_value = {"page_id": 999, "exp": 9999999999}
        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mock.patch.object(CMSDraftPagesViewSet, "_get_page_for_route_slug")
    @mock.patch(f"{MODULE_PATH}.loads")
    def test_detail_view_returns_401_when_payload_missing_page_id(
        self,
        spy_loads: mock.MagicMock,
        spy_get_page_for_route_slug: mock.MagicMock,
    ):
        """
        Given a valid token payload without `page_id`
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned

        Patches:
            `spy_loads`: To return payload without `page_id`.
            `spy_get_page_for_route_slug`: To return a resolved page instance.
        """
        # Given
        spy_get_page_for_route_slug.return_value = mock.Mock(pk=1)
        spy_loads.return_value = {"exp": 9999999999}
        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("payload", [{"page_id": 1}, {"page_id": 1, "exp": 1}])
    @mock.patch(f"{MODULE_PATH}.loads")
    def test_detail_view_returns_401_for_missing_or_expired_exp(
        self,
        spy_loads: mock.MagicMock,
        payload,
    ):
        """
        Given a token payload with missing or expired `exp`
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned

        Patches:
            `spy_loads`: To return payloads with missing/expired `exp`.
        """
        # Given
        spy_loads.return_value = payload
        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mock.patch.object(CMSDraftPagesViewSet, "_render_with_existing_detail_pipeline")
    @mock.patch.object(CMSDraftPagesViewSet, "_get_page_for_route_slug")
    @mock.patch(f"{MODULE_PATH}.loads")
    def test_detail_view_returns_serialized_draft_when_token_is_valid(
        self,
        spy_loads: mock.MagicMock,
        spy_get_page_for_route_slug: mock.MagicMock,
        spy_render_with_existing_detail_pipeline: mock.MagicMock,
    ):
        """
        Given a valid token payload
        When `detail_view()` is called
        Then the existing detail rendering pipeline is used via shim

        Patches:
            `spy_loads`: To return a valid token payload.
            `spy_get_page_for_route_slug`: To return a fake instance with matching page id.
            `spy_render_with_existing_detail_pipeline`: To return deterministic payload.
        """

        # Given
        spy_loads.return_value = {"page_id": 1, "exp": 9999999999}
        spy_get_page_for_route_slug.return_value = mock.Mock(pk=1)
        spy_render_with_existing_detail_pipeline.return_value = Response({"ok": True})

        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request, slug="test-page"
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"ok": True}
        spy_render_with_existing_detail_pipeline.assert_called_once_with(
            request=mock.ANY,
            page=mock.ANY,
        )

    def test_resolve_page_for_response_returns_latest_revision_when_show_draft_true(
        self,
    ):
        """
        Given a page with unpublished changes
        When the shared resolver is called with `show_draft=True`
        Then the latest revision object is returned
        """

        # Given
        draft_object = object()
        latest_revision = mock.Mock()
        latest_revision.as_object.return_value = draft_object
        page = mock.Mock(has_unpublished_changes=True, live=True)
        page.get_latest_revision.return_value = latest_revision

        # When
        resolved_page = CMSDraftPagesViewSet._resolve_page_for_response(
            page=page,
            show_draft=True,
        )

        # Then
        assert resolved_page is draft_object

    def test_resolve_page_for_response_falls_back_to_live_when_no_draft(self):
        """
        Given a page without unpublished changes and with a live version
        When the shared resolver is called with `show_draft=True`
        Then the live specific page is returned
        """

        # Given
        fallback_page = object()
        page = mock.Mock(
            has_unpublished_changes=False,
            live=True,
            specific=fallback_page,
        )

        # When
        resolved_page = CMSDraftPagesViewSet._resolve_page_for_response(
            page=page,
            show_draft=True,
        )

        # Then
        assert resolved_page is fallback_page

    def test_resolve_page_for_response_falls_back_to_live_when_revision_missing(self):
        """
        Given a page with unpublished changes but no latest revision object
        When the shared resolver is called with `show_draft=True`
        Then resolver falls back to live specific page when available
        """
        # Given
        fallback_page = object()
        page = mock.Mock(
            has_unpublished_changes=True,
            live=True,
            specific=fallback_page,
        )
        page.get_latest_revision.return_value = None

        # When
        resolved_page = CMSDraftPagesViewSet._resolve_page_for_response(
            page=page,
            show_draft=True,
        )

        # Then
        assert resolved_page is fallback_page

    def test_resolve_page_for_response_returns_none_when_no_draft_or_live(self):
        """
        Given a page without draft and without live version
        When the shared resolver is called with `show_draft=True`
        Then None is returned
        """
        # Given
        page = mock.Mock(has_unpublished_changes=False, live=False)

        # When
        resolved_page = CMSDraftPagesViewSet._resolve_page_for_response(
            page=page,
            show_draft=True,
        )

        # Then
        assert resolved_page is None

    def test_resolve_page_for_response_returns_specific_when_show_draft_false(self):
        """
        Given a page instance with a specific object
        When resolver is called with default show_draft=False
        Then specific page is returned unchanged
        """
        # Given
        specific_page = object()
        page = mock.Mock(specific=specific_page)

        # When
        resolved_page = CMSDraftPagesViewSet._resolve_page_for_response(page=page)

        # Then
        assert resolved_page is specific_page

    @mock.patch.object(CMSDraftPagesViewSet, "get_queryset")
    def test_get_page_for_route_slug_uses_nested_path_suffix(
        self,
        spy_get_queryset: mock.MagicMock,
    ):
        """
        Given a nested route-style slug
        When page lookup is performed for drafts endpoint
        Then lookup uses url_path suffix matching for nested route

        Patches:
            `spy_get_queryset`: To control queryset filtering result.
        """
        # Given
        queryset = mock.Mock()
        filtered = mock.Mock()
        filtered.first.return_value = mock.sentinel.page
        queryset.filter.return_value = filtered
        spy_get_queryset.return_value = queryset
        viewset = CMSDraftPagesViewSet()

        # When
        page = viewset._get_page_for_route_slug(slug="respiratory-viruses/covid-19")

        # Then
        assert page is mock.sentinel.page
        queryset.filter.assert_called_once_with(
            url_path__endswith="/respiratory-viruses/covid-19/"
        )

    @mock.patch.object(CMSDraftPagesViewSet, "get_queryset")
    def test_get_page_for_route_slug_accepts_leaf_slug_format(
        self,
        spy_get_queryset: mock.MagicMock,
    ):
        """
        Given a leaf-only slug format
        When page lookup is performed for drafts endpoint
        Then lookup still resolves by url_path suffix

        Patches:
            `spy_get_queryset`: To control queryset filtering result.
        """
        # Given
        queryset = mock.Mock()
        filtered = mock.Mock()
        filtered.first.return_value = mock.sentinel.page
        queryset.filter.return_value = filtered
        spy_get_queryset.return_value = queryset
        viewset = CMSDraftPagesViewSet()

        # When
        page = viewset._get_page_for_route_slug(slug="covid-19")

        # Then
        assert page is mock.sentinel.page
        queryset.filter.assert_called_once_with(url_path__endswith="/covid-19/")

    @mock.patch.object(CMSDraftPagesViewSet, "get_queryset")
    def test_get_page_for_route_slug_returns_none_for_empty_slug(
        self,
        spy_get_queryset: mock.MagicMock,
    ):
        """
        Given an empty/blank slug
        When route lookup is attempted
        Then None is returned and no queryset lookup occurs

        Patches:
            `spy_get_queryset`: To assert queryset is not called.
        """
        # Given
        viewset = CMSDraftPagesViewSet()

        # When
        page = viewset._get_page_for_route_slug(slug="/")

        # Then
        assert page is None
        spy_get_queryset.assert_not_called()

    @mock.patch.object(CMSDraftPagesViewSet, "_render_with_existing_detail_pipeline")
    @mock.patch(f"{MODULE_PATH}.loads")
    @mock.patch.object(CMSDraftPagesViewSet, "_get_page_for_route_slug")
    def test_detail_view_accepts_nested_route_slug(
        self,
        spy_get_page_for_route_slug: mock.MagicMock,
        spy_loads: mock.MagicMock,
        spy_render_with_existing_detail_pipeline: mock.MagicMock,
    ):
        """
        Given a nested route-style slug in drafts endpoint path
        When detail view is called
        Then request is resolved and rendered via existing detail pipeline

        Patches:
            `spy_get_page_for_route_slug`: To return a matching page.
            `spy_loads`: To return a valid preview token payload.
            `spy_render_with_existing_detail_pipeline`: To provide response payload.
        """
        # Given
        spy_loads.return_value = {"page_id": 1, "exp": 9999999999}
        spy_get_page_for_route_slug.return_value = mock.Mock(
            pk=1,
            has_unpublished_changes=False,
            live=True,
            specific=mock.sentinel.live_page,
        )
        spy_render_with_existing_detail_pipeline.return_value = Response({"ok": True})

        request = RequestFactory().get(
            "/api/drafts/respiratory-viruses/covid-19/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request,
            slug="respiratory-viruses/covid-19",
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"ok": True}

    @mock.patch(f"{MODULE_PATH}.loads")
    @mock.patch.object(CMSDraftPagesViewSet, "_get_page_for_route_slug")
    def test_detail_view_returns_404_when_route_slug_not_found(
        self,
        spy_get_page_for_route_slug: mock.MagicMock,
        spy_loads: mock.MagicMock,
    ):
        """
        Given valid token but no page matches requested route slug
        When detail view is called
        Then HTTP 404 is returned

        Patches:
            `spy_get_page_for_route_slug`: To simulate route miss.
            `spy_loads`: To return a valid preview token payload.
        """
        # Given
        spy_loads.return_value = {"page_id": 1, "exp": 9999999999}
        spy_get_page_for_route_slug.return_value = None
        request = RequestFactory().get(
            "/api/drafts/unknown-route/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request,
            slug="unknown-route",
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @mock.patch.object(CMSDraftPagesViewSet, "_render_with_existing_detail_pipeline")
    @mock.patch(f"{MODULE_PATH}.loads")
    @mock.patch.object(CMSDraftPagesViewSet, "_get_page_for_route_slug")
    def test_detail_view_returns_404_when_no_draft_or_live_page_available(
        self,
        spy_get_page_for_route_slug: mock.MagicMock,
        spy_loads: mock.MagicMock,
        spy_render_with_existing_detail_pipeline: mock.MagicMock,
    ):
        """
        Given a valid token and matching route slug
        When page has neither draft changes nor live version
        Then HTTP 404 is returned and render pipeline is not called

        Patches:
            `spy_get_page_for_route_slug`: To return non-live/non-draft page.
            `spy_loads`: To return a valid preview token payload.
            `spy_render_with_existing_detail_pipeline`: To assert no render call.
        """
        # Given
        spy_loads.return_value = {"page_id": 1, "exp": 9999999999}
        spy_get_page_for_route_slug.return_value = mock.Mock(
            pk=1,
            has_unpublished_changes=False,
            live=False,
        )
        request = RequestFactory().get(
            "/api/drafts/test-page/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(
            request,
            slug="test-page",
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        spy_render_with_existing_detail_pipeline.assert_not_called()

    @mock.patch.object(PagesAPIViewSet, "get_object")
    def test_get_object_falls_back_to_parent_when_no_forced_page(
        self,
        spy_parent_get_object: mock.MagicMock,
    ):
        """
        Given no forced detail page on the viewset instance
        When get_object() is called
        Then it falls back to PagesAPIViewSet.get_object()

        Patches:
            `spy_parent_get_object`: To control parent object retrieval.
        """
        # Given
        sentinel_object = object()
        spy_parent_get_object.return_value = sentinel_object
        viewset = CMSDraftPagesViewSet()

        # When
        returned_object = viewset.get_object()

        # Then
        assert returned_object is sentinel_object

    def test_get_object_uses_forced_detail_page_when_set(self):
        """
        Given a forced detail page on the viewset instance
        When get_object() is called
        Then forced page is returned without parent lookup
        """
        # Given
        forced_page = object()
        viewset = CMSDraftPagesViewSet()
        viewset._forced_detail_page = forced_page

        # When
        returned_object = viewset.get_object()

        # Then
        assert returned_object is forced_page

    @mock.patch.object(PagesAPIViewSet, "detail_view")
    def test_render_with_existing_detail_pipeline_clears_forced_page_on_success(
        self,
        spy_parent_detail_view: mock.MagicMock,
    ):
        """
        Given a resolved page for draft response
        When rendering through existing detail pipeline succeeds
        Then parent detail view is called and forced page state is cleared

        Patches:
            `spy_parent_detail_view`: To control parent detail response.
        """
        # Given
        expected_response = Response({"ok": True})
        spy_parent_detail_view.return_value = expected_response
        viewset = CMSDraftPagesViewSet()
        request = RequestFactory().get("/api/drafts/test-page/")
        page = mock.Mock(pk=123)

        # When
        response = viewset._render_with_existing_detail_pipeline(
            request=request,
            page=page,
        )

        # Then
        assert response is expected_response
        spy_parent_detail_view.assert_called_once_with(request=request, pk=123)
        assert viewset._forced_detail_page is None

    @mock.patch.object(PagesAPIViewSet, "detail_view")
    def test_render_with_existing_detail_pipeline_clears_forced_page_on_error(
        self,
        spy_parent_detail_view: mock.MagicMock,
    ):
        """
        Given a resolved page for draft response
        When rendering through existing detail pipeline raises
        Then forced page state is still cleared in finally block

        Patches:
            `spy_parent_detail_view`: To force raised error from parent detail.
        """
        # Given
        spy_parent_detail_view.side_effect = RuntimeError("boom")
        viewset = CMSDraftPagesViewSet()
        request = RequestFactory().get("/api/drafts/test-page/")
        page = mock.Mock(pk=456)

        # When / Then
        with pytest.raises(RuntimeError, match="boom"):
            viewset._render_with_existing_detail_pipeline(
                request=request,
                page=page,
            )

        assert viewset._forced_detail_page is None


class TestCMSPagesAPIViewSet:
    def test_base_serializer_class_is_set_with_correct_serializer(self):
        """
        Given an instance of the `CMSPagesAPIViewSet`
        When the `base_serializer_class` attribute is called
        Then the `ListablePageSerializer` class is returned
        """
        # Given
        pages_viewset = CMSPagesAPIViewSet()

        # When
        base_serializer_class = pages_viewset.base_serializer_class

        # Then
        assert base_serializer_class is ListablePageSerializer

    def test_listing_default_fields_is_set_with_show_in_menus(self):
        """
        Given an instance of the `CMSPagesAPIViewSet`
        When the `listing_default_fields` attribute is called
        Then "show_in_menus" is found within the returned list of fields
        """
        # Given
        pages_viewset = CMSPagesAPIViewSet()

        # When
        listing_default_fields = pages_viewset.listing_default_fields

        # Then
        assert "show_in_menus" in listing_default_fields

    @mock.patch("wagtail.api.v2.views.PagesAPIViewSet.get_queryset")
    def test_get_queryset_returns_specific_models(
        self,
        spy_pages_api_get_queryset: mock.MagicMock,
    ):
        """
        Given the normal pages viewset
        When get_queryset() is called
        Then base queryset is converted to specific model instances

        Patches:
            `spy_pages_api_get_queryset`: To provide base queryset mock.
        """
        # Given
        expected_queryset = object()
        queryset = mock.Mock()
        queryset.specific.return_value = expected_queryset
        spy_pages_api_get_queryset.return_value = queryset
        viewset = CMSPagesAPIViewSet()

        # When
        returned_queryset = viewset.get_queryset()

        # Then
        assert returned_queryset is expected_queryset
        spy_pages_api_get_queryset.assert_called_once_with()
        queryset.specific.assert_called_once_with()

    @mock.patch("wagtail.api.v2.views.PagesAPIViewSet.detail_view")
    def test_detail_view_delegates_to_existing_wagtail_detail_pipeline(
        self,
        spy_pages_api_detail_view: mock.MagicMock,
    ):
        """
        Given the normal pages endpoint
        When `detail_view()` is called on normal pages endpoint
        Then the existing Wagtail detail pipeline is used unchanged

        Patches:
            `spy_pages_api_detail_view`: To assert delegation and response.
        """
        # Given
        spy_pages_api_detail_view.return_value = Response({"ok": True})
        request = RequestFactory().get("/api/pages/1/")

        # When
        response = CMSPagesAPIViewSet.as_view({"get": "detail_view"})(request, pk=1)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"ok": True}
        spy_pages_api_detail_view.assert_called_once_with(request=mock.ANY, pk=1)

    @mock.patch("wagtail.api.v2.views.PagesAPIViewSet.listing_view")
    def test_listing_view_delegates_to_existing_wagtail_listing_pipeline(
        self,
        spy_pages_api_listing_view: mock.MagicMock,
    ):
        """
        Given the normal pages endpoint
        When `listing_view()` is called
        Then the existing Wagtail listing pipeline is used unchanged

        Patches:
            `spy_pages_api_listing_view`: To assert delegation and response.
        """
        # Given
        spy_pages_api_listing_view.return_value = Response({"items": []})
        request = RequestFactory().get("/api/pages/")

        # When
        response = CMSPagesAPIViewSet.as_view({"get": "listing_view"})(request)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"items": []}
        spy_pages_api_listing_view.assert_called_once_with(request=mock.ANY)

    def test_only_normal_pages_detail_view_is_cache_wrapped(self):
        """
        Given normal and draft CMS detail view methods
        When checking cache decorator wrapping
        Then only normal pages detail view is cache-wrapped
        """
        assert hasattr(CMSPagesAPIViewSet.detail_view, "__wrapped__")
        assert not hasattr(CMSDraftPagesViewSet.detail_view, "__wrapped__")
