from types import SimpleNamespace

from public_api.auth import (
    get_permission_sets_for_request,
    is_authenticated_request,
)

PERMISSION_SETS = {
    "permission_sets": [],
    "summary": {"has_global_access": False},
}


def test_request_without_authenticated_credentials_has_no_permissions():
    request = SimpleNamespace(
        auth=None,
        user=SimpleNamespace(permission_sets=PERMISSION_SETS),
    )

    assert not is_authenticated_request(request)
    assert get_permission_sets_for_request(request) is None


def test_authenticated_request_uses_its_users_permissions():
    request = SimpleNamespace(
        auth="valid-jwt",
        user=SimpleNamespace(permission_sets=PERMISSION_SETS),
    )

    assert is_authenticated_request(request)
    assert get_permission_sets_for_request(request) is PERMISSION_SETS


def test_authenticated_request_without_user_permissions_has_no_permissions():
    request = SimpleNamespace(auth="valid-jwt", user=SimpleNamespace())

    assert is_authenticated_request(request)
    assert get_permission_sets_for_request(request) is None
