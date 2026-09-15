from unittest import mock

from public_api.auth import (
    get_permission_sets_for_request,
    is_authenticated_request,
)

PERMISSION_SETS = {
    "permission_sets": [],
    "summary": {"has_global_access": False},
}
AUTH_ENABLED_PATH = "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled"


def test_request_without_authenticated_credentials_has_no_permissions():
    request = mock.Mock(
        auth=None,
        user=mock.Mock(permission_sets=PERMISSION_SETS),
    )

    with mock.patch(AUTH_ENABLED_PATH, return_value=True):
        assert not is_authenticated_request(request)
        assert get_permission_sets_for_request(request) is None


def test_authenticated_request_uses_its_users_permissions():
    request = mock.Mock(
        auth="valid-jwt",
        user=mock.Mock(permission_sets=PERMISSION_SETS),
    )

    with mock.patch(AUTH_ENABLED_PATH, return_value=True):
        assert is_authenticated_request(request)
        assert get_permission_sets_for_request(request) is PERMISSION_SETS


def test_authenticated_request_without_user_permissions_has_no_permissions():
    request = mock.Mock(auth="valid-jwt", user=mock.Mock(permission_sets=None))

    with mock.patch(AUTH_ENABLED_PATH, return_value=True):
        assert is_authenticated_request(request)
        assert get_permission_sets_for_request(request) is None


def test_request_has_no_permisisons_when_authentication_is_disabled():
    request = mock.Mock(
        auth="valid-jwt",
        user=mock.Mock(permission_sets=PERMISSION_SETS),
    )

    with mock.patch(AUTH_ENABLED_PATH, return_value=False):
        assert not is_authenticated_request(request)
        assert get_permission_sets_for_request(request) is None