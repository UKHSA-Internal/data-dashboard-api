import pytest
from django.test import RequestFactory
from rest_framework import status

from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.dashboard.viewsets import CMSDraftPagesViewSet, CMSPagesAPIViewSet


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

    def test_detail_view_returns_401_without_valid_bearer_authorization(self):
        request = RequestFactory().get("/api/drafts/1/")

        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_401_when_token_cannot_be_loaded(self, monkeypatch):
        def raise_bad_token(token, salt):
            raise ValueError("bad token")

        monkeypatch.setattr("cms.dashboard.viewsets.loads", raise_bad_token)
        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_401_when_page_id_does_not_match(self, monkeypatch):
        monkeypatch.setattr(
            "cms.dashboard.viewsets.loads",
            lambda token, salt: {"page_id": 999, "exp": 9999999999},
        )
        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("payload", [{"page_id": 1}, {"page_id": 1, "exp": 1}])
    def test_detail_view_returns_401_for_missing_or_expired_exp(self, monkeypatch, payload):
        monkeypatch.setattr("cms.dashboard.viewsets.loads", lambda token, salt: payload)
        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_serialized_draft_when_token_is_valid(self, monkeypatch):
        class FakeInstance:
            def get_latest_revision_as_object(self):
                return object()

        class FakeSerializer:
            data = {"ok": True}

        monkeypatch.setattr(
            "cms.dashboard.viewsets.loads",
            lambda token, salt: {"page_id": 1, "exp": 9999999999},
        )
        monkeypatch.setattr(
            CMSDraftPagesViewSet,
            "get_object",
            lambda self: FakeInstance(),
        )
        monkeypatch.setattr(
            CMSDraftPagesViewSet,
            "get_serializer",
            lambda self, instance: FakeSerializer(),
        )

        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"ok": True}


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
