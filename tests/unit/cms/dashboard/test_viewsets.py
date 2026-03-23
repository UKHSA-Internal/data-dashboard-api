import pytest
from unittest.mock import patch, MagicMock
from rest_framework.request import Request
from django.core.signing import BadSignature as DjangoBadSignature
from types import SimpleNamespace

from cms.dashboard.serializers import ListablePageSerializer
from cms.dashboard.viewsets import (
    CMSDraftPagesViewSet,
    CMSPagesAPIViewSet,
    PagesAPIViewSet,
)


class TestCMSDraftPagesViewSet:
    @patch(
        "cms.dashboard.viewsets.loads", return_value={"exp": 9999999999, "page_id": 2}
    )
    def test_detail_view_returns_401_if_page_id_mismatch(self, mock_loads):
        """
        Given a draft page with a mismatched page_id in the token
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        fake_instance = MagicMock()
        fake_instance.pk = 1
        fake_instance.get_latest_revision.return_value = None
        viewset.get_queryset = MagicMock(
            return_value=MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=fake_instance))
                )
            )
        )
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch(
        "cms.dashboard.viewsets.loads", return_value={"exp": 9999999999, "page_id": 1}
    )
    def test_detail_view_returns_200_with_latest_revision(self, mock_loads):
        """
        Given a draft page with a valid token and a latest revision
        When detail_view is called
        Then a 200 response is returned with the latest revision data
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = MagicMock(
            as_object=MagicMock(return_value="draft_page")
        )
        viewset.get_queryset = MagicMock(
            return_value=MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=fake_instance))
                )
            )
        )
        viewset.get_serializer = MagicMock(return_value=MagicMock(data={"foo": "bar"}))
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 200
        assert response.data == {"foo": "bar"}

    @patch(
        "cms.dashboard.viewsets.loads", return_value={"exp": 9999999999, "page_id": 1}
    )
    def test_detail_view_returns_200_with_published_version(self, mock_loads):
        """
        Given a draft page with a valid token and no latest revision
        When detail_view is called
        Then a 200 response is returned with the published version data
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = None
        viewset.get_queryset = MagicMock(
            return_value=MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=fake_instance))
                )
            )
        )
        viewset.get_serializer = MagicMock(
            return_value=MagicMock(data={"foo": "published"})
        )
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 200
        assert response.data == {"foo": "published"}

    @patch(
        "cms.dashboard.viewsets.loads", return_value={"exp": 9999999999, "page_id": 1}
    )
    def test_detail_view_returns_404_if_page_not_found(self, mock_loads):
        """
        Given a valid token but the page is not found
        When detail_view is called
        Then a 404 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        viewset.get_queryset = MagicMock(
            return_value=MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=None))
                )
            )
        )
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 404

    @patch("cms.dashboard.viewsets.loads", return_value={"exp": None, "page_id": 1})
    def test_detail_view_returns_401_if_exp_is_none(self, mock_loads):
        """
        Given a token with no exp value
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.loads", return_value={"exp": 1, "page_id": 1})
    @patch("cms.dashboard.viewsets.timezone")
    def test_detail_view_returns_401_if_expired(self, mock_tz, mock_loads):
        """
        Given a token with an expired exp value
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        mock_tz.now.return_value.timestamp.return_value = 2
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    def test_detail_view_returns_401_if_no_auth(self):
        """
        Given no authentication header
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {}
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    def test_detail_view_returns_401_if_auth_not_bearer(self):
        """
        Given an authentication header that is not Bearer
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "notbearer faketoken"}
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.loads", return_value={"exp": 0, "page_id": 1})
    def test_detail_view_returns_401_for_expired_token(self, mock_loads):
        """
        Given a token with an expired exp value (in the past)
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        viewset = CMSDraftPagesViewSet()
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.settings")
    def test_detail_view_previews_disabled_returns_403(self, mock_settings):
        """
        Given PAGE_PREVIEWS_ENABLED is False
        When detail_view is called
        Then a 403 response is returned with the appropriate message
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        mock_settings.PAGE_PREVIEWS_ENABLED = False
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 403
        assert "Page previews are disabled" in response.data["detail"]

    @patch(
        "cms.dashboard.viewsets.PagesAPIViewSet.get_object", return_value="parent_obj"
    )
    def test_get_object_calls_super_when_forced_page_none(self, mock_parent):
        """
        Given _forced_detail_page is None
        When get_object is called
        Then the parent get_object is called and its result is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        viewset._forced_detail_page = None
        # When
        result = viewset.get_object()
        # Then
        assert result == "parent_obj"
        mock_parent.assert_called_once()

    # (Duplicate imports removed)

    @patch(
        "cms.dashboard.viewsets.loads", return_value={"exp": 9999999999, "page_id": 1}
    )
    def test_happy_path_returns_200(self, mock_loads):
        """Happy path: detail_view returns 200 with a resolved page, fully mocked."""
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = MagicMock(
            as_object=MagicMock(return_value=fake_instance)
        )
        fake_instance.title = "Test page"
        viewset.get_queryset = MagicMock(
            return_value=MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=fake_instance))
                )
            )
        )
        fake_serializer = MagicMock()
        fake_serializer.data = {"title": fake_instance.title}
        viewset.get_serializer = MagicMock(return_value=fake_serializer)
        response = viewset.detail_view(request=request, pk=1)
        assert response.status_code == 200
        assert response.data["title"] == "Test page"

    def test_missing_auth_returns_401(self):
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {}
        response = viewset.detail_view(request=request, pk=1)
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.loads", side_effect=DjangoBadSignature)
    def test_invalid_token_returns_401(self, mock_loads):
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer fake"}
        response = viewset.detail_view(request=request, pk=1)
        assert response.status_code == 401

    @patch(
        "cms.dashboard.viewsets.loads", return_value={"exp": 9999999999, "page_id": 1}
    )
    @patch.object(CMSDraftPagesViewSet, "get_queryset")
    def test_resolve_returns_none_404(self, mock_get_queryset, mock_loads, settings):
        settings.PAGE_PREVIEWS_ENABLED = True
        mock_get_queryset.return_value.filter.return_value.first.return_value = None
        viewset = CMSDraftPagesViewSet()
        request = MagicMock(spec=Request)
        request.headers = {"x-draft-auth": "Bearer faketoken"}
        response = viewset.detail_view(request=request, pk=1)
        assert response.status_code == 404

    @patch("cms.dashboard.viewsets.PagesAPIViewSet.listing_view")
    def test_listing_view_calls_super(self, mock_super_listing):
        viewset = CMSPagesAPIViewSet()
        request = MagicMock(spec=Request)
        expected_response = MagicMock()
        mock_super_listing.return_value = expected_response
        response = CMSPagesAPIViewSet.listing_view.__wrapped__(viewset, request=request)
        _, called_kwargs = mock_super_listing.call_args
        assert called_kwargs["request"] is request
        assert response == expected_response

    def test_base_serializer_class_is_set_with_correct_serializer(self):
        draft_pages_viewset = CMSDraftPagesViewSet()
        base_serializer_class = draft_pages_viewset.base_serializer_class
        assert base_serializer_class is ListablePageSerializer

    def test_permission_classes_has_no_api_key_constraint(self):
        draft_pages_viewset = CMSDraftPagesViewSet()
        permission_classes = draft_pages_viewset.permission_classes
        assert permission_classes == []

    @patch(
        "cms.dashboard.viewsets.PagesAPIViewSet.get_queryset",
        return_value=MagicMock(specific=MagicMock(return_value=[])),
    )
    def test_cms_pages_api_viewset_get_queryset_calls_super(self, mock_super):
        viewset = CMSPagesAPIViewSet()
        result = viewset.get_queryset()
        mock_super.assert_called_once()
        assert result == []


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
