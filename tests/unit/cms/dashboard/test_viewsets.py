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
        """
        Given a request with no bearer authorization header
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned
        """
        # Given
        request = RequestFactory().get("/api/drafts/1/")

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_401_when_token_cannot_be_loaded(self, monkeypatch):
        """
        Given a request with a bearer token that cannot be decoded
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned
        """
        # Given
        def raise_bad_token(token, salt):
            raise ValueError("bad token")

        monkeypatch.setattr("cms.dashboard.viewsets.loads", raise_bad_token)
        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_401_when_page_id_does_not_match(self, monkeypatch):
        """
        Given a token payload whose `page_id` does not match the request id
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned
        """
        # Given
        monkeypatch.setattr(
            "cms.dashboard.viewsets.loads",
            lambda token, salt: {"page_id": 999, "exp": 9999999999},
        )
        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("payload", [{"page_id": 1}, {"page_id": 1, "exp": 1}])
    def test_detail_view_returns_401_for_missing_or_expired_exp(
        self, monkeypatch, payload
    ):
        """
        Given a token payload with missing or expired `exp`
        When `detail_view()` is called
        Then HTTP 401 Unauthorized is returned
        """
        # Given
        monkeypatch.setattr("cms.dashboard.viewsets.loads", lambda token, salt: payload)
        request = RequestFactory().get(
            "/api/drafts/1/",
            HTTP_AUTHORIZATION="Bearer token",
        )

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_view_returns_serialized_draft_when_token_is_valid(
        self, monkeypatch
    ):
        """
        Given a valid token payload and a latest revision object
        When `detail_view()` is called
        Then HTTP 200 OK and serialized data are returned
        """
        # Given
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

        # When
        response = CMSDraftPagesViewSet.as_view({"get": "detail_view"})(request, pk=1)

        # Then
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
