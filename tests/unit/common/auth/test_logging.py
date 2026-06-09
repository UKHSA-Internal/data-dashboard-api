from unittest import mock

import pytest

from common.auth.logging import log_user_permissions


@pytest.mark.parametrize(
    "permission_sets, expected_has_global_access",
    [
        (
            {
                "permission_sets": [],
                "summary": {"total_permission_sets": 2, "has_global_access": True},
            },
            True,
        ),
        (
            {
                "permission_sets": [],
                "summary": {"total_permission_sets": 1, "has_global_access": False},
            },
            False,
        ),
        (
            {
                "permission_sets": [],
                "summary": {"total_permission_sets": 0, "has_global_access": False},
            },
            False,
        ),
    ],
)
@mock.patch("common.auth.logging.logger.info")
def test_log_user_permissions(
    mocked_logger_info: mock.MagicMock,
    permission_sets,
    expected_has_global_access,
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
    log_messages = [call.args[0] for call in mocked_logger_info.call_args_list]
    expected_count = permission_sets["summary"]["total_permission_sets"]

    assert any(
        f"total permission sets {expected_count}" in message for message in log_messages
    )
    assert (
        any("global access" in message for message in log_messages)
        is expected_has_global_access
    )
