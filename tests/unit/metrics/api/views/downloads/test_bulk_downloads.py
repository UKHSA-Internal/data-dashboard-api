from unittest import mock

from metrics.api.views.downloads.bulk_downloads import (
    BulkDownloadsView,
    get_permission_sets_for_request,
)

MODULE_PATH = "metrics.api.views.downloads.bulk_downloads"


def _build_request(*, auth: mock.MagicMock | None, permission_sets=None) -> mock.Mock:
    user = mock.Mock(spec=["permission_sets"])
    user.permission_sets = permission_sets
    return mock.Mock(
        query_params={"file_format": "csv"},
        auth=auth,
        user=user,
    )


class TestGetPermissionSetsForRequest:
    @mock.patch(f"{MODULE_PATH}.auth")
    def test_returns_none_when_auth_is_not_enabled(self, mocked_auth: mock.MagicMock):
        """
        Given authentication which is not enabled
        When `get_permission_sets_for_request()` is called
        Then None is returned
        """
        # Given
        mocked_auth.AUTH_ENABLED = False
        mocked_permission_sets = mock.Mock()
        request = _build_request(
            auth=mock.Mock(), permission_sets=mocked_permission_sets
        )

        # When
        permission_sets = get_permission_sets_for_request(request=request)

        # Then
        assert permission_sets is None

    @mock.patch(f"{MODULE_PATH}.auth")
    def test_returns_none_for_unauthenticated_request(
        self, mocked_auth: mock.MagicMock
    ):
        """
        Given authentication which is enabled
        And a request made by an anonymous/unauthenticated user
        When `get_permission_sets_for_request()` is called
        Then None is returned
        """
        # Given
        mocked_auth.AUTH_ENABLED = True
        request = _build_request(auth=None, permission_sets=mock.Mock())

        # When
        permission_sets = get_permission_sets_for_request(request=request)

        # Then
        assert permission_sets is None

    @mock.patch(f"{MODULE_PATH}.auth")
    def test_returns_permission_sets_of_authenticated_user(
        self, mocked_auth: mock.MagicMock
    ):
        """
        Given authentication which is enabled
        And a request made by an authenticated user
        When `get_permission_sets_for_request()` is called
        Then the permission sets of that user are returned
        """
        # Given
        mocked_auth.AUTH_ENABLED = True
        mocked_permission_sets = mock.Mock()
        request = _build_request(
            auth=mock.Mock(), permission_sets=mocked_permission_sets
        )

        # When
        permission_sets = get_permission_sets_for_request(request=request)

        # Then
        assert permission_sets == mocked_permission_sets


class TestBulkDownloadsView:
    @mock.patch(f"{MODULE_PATH}.get_bulk_downloads_archive")
    @mock.patch(f"{MODULE_PATH}.get_permission_sets_for_request")
    def test_delegates_permission_sets_of_request(
        self,
        mocked_get_permission_sets_for_request: mock.MagicMock,
        spy_get_bulk_downloads_archive: mock.MagicMock,
    ):
        """
        Given a request made to the bulk downloads endpoint
        When the `GET` method is called from the `BulkDownloadsView`
        Then the permission sets of the request
            are passed to `get_bulk_downloads_archive()`
        """
        # Given
        request = _build_request(auth=mock.Mock())
        mocked_permission_sets = mocked_get_permission_sets_for_request.return_value
        spy_get_bulk_downloads_archive.return_value = {
            "zip_file_data": b"",
            "zip_file_name": "downloads.zip",
        }

        # When
        BulkDownloadsView.get(request)

        # Then
        mocked_get_permission_sets_for_request.assert_called_once_with(request=request)
        spy_get_bulk_downloads_archive.assert_called_once_with(
            file_format="csv", permission_sets=mocked_permission_sets
        )
