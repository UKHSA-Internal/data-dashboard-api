from unittest import mock

import pytest

from common.auth.logging import log_user_permissions


@pytest.mark.parametrize(
    "permission_sets, expected_calls",
    [
        (
            {
                "summary": {
                    "total_permission_sets": 2,
                    "has_global_access": False,
                }
            },
            [
                mock.call("User %s has total permission sets: %s", "user-1", 2),
                mock.call("User %s has global access: %s", "user-1", False),
            ],
        ),
        (
            {
                "summary": {
                    "total_permission_sets": 3,
                    "has_global_access": True,
                }
            },
            [
                mock.call("User %s has total permission sets: %s", "user-1", 3),
                mock.call("User %s has global access: %s", "user-1", True),
            ],
        ),
        (
            [{"theme": {"id": "1"}}],
            [
                mock.call("User %s has total permission sets: %s", "user-1", 1),
                mock.call("User %s has global access: %s", "user-1", False),
            ],
        ),
    ],
)
@mock.patch("common.auth.logging.logger.info")
def test_log_user_permissions(
    mocked_logger_info: mock.MagicMock,
    permission_sets,
    expected_calls,
):
    """
    Given different user permission-set payloads
    When log_user_permissions() is called
    Then the expected log calls are made
    """

    # Given

    user = mock.Mock(username="user-1")

    if permission_sets is not None:
        user.permission_sets = permission_sets

    # When
    log_user_permissions(user)

    # Then
    assert mocked_logger_info.call_args_list == expected_calls
