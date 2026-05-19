import pytest

from unittest.mock import patch, MagicMock
from rest_framework.request import Request
from django.core.signing import BadSignature as DjangoBadSignature

from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.dashboard.viewsets import (
    CMSDraftPagesViewSet,
    CMSPagesAPIViewSet,
)

from cms.dashboard.serializers import ListablePageSerializer
from cms.dashboard.viewsets import (
    BaseCMSPagesAPIViewSet,
    CMSDraftPagesViewSet,
    CMSPagesAPIViewSet,
    PagesAPIViewSet,
)


class TestCMSDraftPagesViewSet:
    @staticmethod
    def _build_request(*, auth_header: str | None = "Bearer faketoken") -> MagicMock:
        request = MagicMock(spec=Request)
        request.headers = {"x-cms-auth": auth_header} if auth_header is not None else {}
        return request

    @staticmethod
    def _mock_queryset_first(viewset: CMSDraftPagesViewSet, instance) -> None:
        viewset.get_queryset = MagicMock(
            return_value=MagicMock(
                filter=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=instance))
                )
            )
        )

    @patch(
        "cms.dashboard.viewsets.get_cms_auth_payload",
        return_value={"page_id": 1, "embargo_time": 1711456200},
    )
    @patch(
        "cms.dashboard.viewsets.validate_preview_hmac_token",
        return_value=True,
    )
    def test_detail_view_includes_embargo_time_with_latest_revision(
        self, mock_validate, mock_get_payload, settings
    ):
        settings.PAGE_PREVIEWS_ENABLED = True
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = MagicMock(
            as_object=MagicMock(return_value="draft_page")
        )
        self._mock_queryset_first(viewset, fake_instance)
        viewset.get_serializer = MagicMock(return_value=MagicMock(data={"foo": "bar"}))

        response = viewset.detail_view(request=request, pk=1)

        assert response.status_code == 200
        assert response.data == {"foo": "bar", "embargo_time": 1711456200}

    @patch(
        "cms.dashboard.viewsets.validate_preview_hmac_token",
        return_value={"page_id": 1, "embargo_time": None},
    )
    def test_detail_view_includes_null_embargo_time_with_published_version(
        self, mock_validate, settings
    ):
        settings.PAGE_PREVIEWS_ENABLED = True
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = None
        self._mock_queryset_first(viewset, fake_instance)
        viewset.get_serializer = MagicMock(
            return_value=MagicMock(data={"foo": "published"})
        )

        response = viewset.detail_view(request=request, pk=1)

        assert response.status_code == 200
        assert response.data == {"foo": "published", "embargo_time": None}

    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=False)
    def test_detail_view_returns_401_if_page_id_mismatch(self, mock_validate):
        """
        Given a draft page with a mismatched page_id in the token
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
        fake_instance = MagicMock()
        fake_instance.pk = 1
        fake_instance.get_latest_revision.return_value = None
        self._mock_queryset_first(viewset, fake_instance)
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.get_cms_auth_payload", return_value={})
    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=True)
    def test_detail_view_returns_200_with_latest_revision(
        self, mock_validate, mock_get_payload
    ):
        """
        Given a draft page with a valid token and a latest revision
        When detail_view is called
        Then a 200 response is returned with the latest revision data
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = MagicMock(
            as_object=MagicMock(return_value="draft_page")
        )
        self._mock_queryset_first(viewset, fake_instance)
        viewset.get_serializer = MagicMock(return_value=MagicMock(data={"foo": "bar"}))
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 200
        assert response.data == {"foo": "bar", "embargo_time": None}

    @patch("cms.dashboard.viewsets.get_cms_auth_payload", return_value={})
    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=True)
    def test_detail_view_returns_200_with_published_version(
        self, mock_validate, mock_get_payload
    ):
        """
        Given a draft page with a valid token and no latest revision
        When detail_view is called
        Then a 200 response is returned with the published version data
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
        fake_instance = MagicMock()
        fake_instance.get_latest_revision.return_value = None
        self._mock_queryset_first(viewset, fake_instance)
        viewset.get_serializer = MagicMock(
            return_value=MagicMock(data={"foo": "published"})
        )
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 200
        assert response.data == {"foo": "published", "embargo_time": None}

    @patch("cms.dashboard.viewsets.get_cms_auth_payload", return_value={})
    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=True)
    def test_detail_view_returns_404_if_page_not_found(
        self, mock_validate, mock_get_payload
    ):
        """
        Given a valid token but the page is not found
        When detail_view is called
        Then a 404 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
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

    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=False)
    def test_detail_view_returns_401_if_exp_is_none(self, mock_validate):
        """
        Given a token with no exp value
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=False)
    def test_detail_view_returns_401_if_expired(self, mock_validate):
        """
        Given a token with an expired exp value
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
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
        request = self._build_request(auth_header=None)
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
        request = self._build_request(auth_header="notbearer faketoken")
        # When
        response = viewset.detail_view(request=request, pk=1)
        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=False)
    def test_detail_view_returns_401_for_expired_token(self, mock_validate):
        """
        Given a token with an expired exp value (in the past)
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        request = self._build_request()
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
        request = self._build_request()
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

    @patch("cms.dashboard.viewsets.get_cms_auth_payload", return_value={})
    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=True)
    def test_happy_path_returns_200(self, mock_validate, mock_get_payload):
        """
        Given a valid token and a resolvable draft page
        When detail_view is called
        Then a 200 response with serialized page data is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()
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

        # When
        response = viewset.detail_view(request=request, pk=1)

        # Then
        assert response.status_code == 200
        assert response.data["title"] == "Test page"

    def test_missing_auth_returns_401(self):
        """
        Given a request with no auth header
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request(auth_header=None)

        # When
        response = viewset.detail_view(request=request, pk=1)

        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=False)
    def test_invalid_token_returns_401(self, mock_validate):
        """
        Given a request with an invalid bearer token
        When detail_view is called
        Then a 401 response is returned
        """
        # Given
        viewset = CMSDraftPagesViewSet()
        request = self._build_request(auth_header="Bearer fake")

        # When
        response = viewset.detail_view(request=request, pk=1)

        # Then
        assert response.status_code == 401

    @patch("cms.dashboard.viewsets.get_cms_auth_payload", return_value={})
    @patch("cms.dashboard.viewsets.validate_preview_hmac_token", return_value=True)
    @patch.object(CMSDraftPagesViewSet, "get_queryset")
    def test_resolve_returns_none_404(
        self, mock_get_queryset, mock_validate, mock_get_payload, settings
    ):
        """
        Given a valid token but no matching page in the queryset
        When detail_view is called
        Then a 404 response is returned
        """
        # Given
        settings.PAGE_PREVIEWS_ENABLED = True
        mock_get_queryset.return_value.filter.return_value.first.return_value = None
        viewset = CMSDraftPagesViewSet()
        request = self._build_request()

        # When
        response = viewset.detail_view(request=request, pk=1)

        # Then
        assert response.status_code == 404

    @patch("cms.dashboard.viewsets.PagesAPIViewSet.listing_view")
    def test_listing_view_calls_super(self, mock_super_listing):
        """
        Given a CMS pages viewset and request
        When listing_view is invoked through the wrapped method
        Then the parent listing_view receives the same request and its response is returned
        """
        # Given
        viewset = CMSPagesAPIViewSet()
        request = MagicMock(spec=Request)
        expected_response = MagicMock()
        mock_super_listing.return_value = expected_response

        # When
        response = CMSPagesAPIViewSet.listing_view.__wrapped__(viewset, request=request)

        # Then
        _, called_kwargs = mock_super_listing.call_args
        assert called_kwargs["request"] is request
        assert response == expected_response

    def test_base_serializer_class_is_set_with_correct_serializer(self):
        """
        Given a CMS draft pages viewset instance
        When base_serializer_class is accessed
        Then ListablePageSerializer is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        base_serializer_class = draft_pages_viewset.base_serializer_class

        # Then
        assert base_serializer_class is ListablePageSerializer

    def test_permission_classes_has_no_api_key_constraint(self):
        """
        Given a CMS draft pages viewset instance
        When permission_classes is accessed
        Then no API key constraint is present
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        permission_classes = draft_pages_viewset.permission_classes

        # Then
        assert permission_classes == []

    @patch(
        "cms.dashboard.viewsets.PagesAPIViewSet.get_queryset",
        return_value=MagicMock(specific=MagicMock(return_value=[])),
    )
    def test_cms_pages_api_viewset_get_queryset_calls_super(self, mock_super):
        """
        Given the parent get_queryset returns a queryset supporting specific()
        When get_queryset is called on CMSPagesAPIViewSet
        Then the parent method is called and the specific queryset is returned
        """
        # Given
        viewset = CMSPagesAPIViewSet()

        # When
        result = viewset.get_queryset()

        # Then
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

    @patch("cms.dashboard.viewsets.PagesAPIViewSet.detail_view")
    def test_base_detail_view_calls_super_with_pk(self, mock_super_detail_view):
        """
        Given a base CMS pages viewset and request
        When detail_view is called with a pk
        Then the parent detail_view is called with the same request and pk
        """
        # Given
        viewset = BaseCMSPagesAPIViewSet()
        request = MagicMock(spec=Request)
        expected_response = MagicMock()
        mock_super_detail_view.return_value = expected_response

        # When
        response = viewset.detail_view(request=request, pk=123)

        # Then
        _, called_kwargs = mock_super_detail_view.call_args
        assert called_kwargs["request"] is request
        assert called_kwargs["pk"] == 123
        assert response == expected_response

    @patch("cms.dashboard.viewsets.BaseCMSPagesAPIViewSet.detail_view")
    def test_cms_pages_detail_view_calls_base(self, mock_base_detail_view):
        """
        Given a CMS pages viewset and request
        When detail_view is invoked through the wrapped method
        Then the base detail_view receives request and pk, and its response is returned
        """
        # Given
        viewset = CMSPagesAPIViewSet()
        request = MagicMock(spec=Request)
        expected_response = MagicMock()
        mock_base_detail_view.return_value = expected_response

        # When
        response = CMSPagesAPIViewSet.detail_view.__wrapped__(
            viewset, request=request, pk=123
        )

        # Then
        mock_base_detail_view.assert_called_once_with(request, 123)
        assert response == expected_response
