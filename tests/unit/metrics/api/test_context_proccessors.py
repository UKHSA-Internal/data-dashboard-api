from typing import Dict
from unittest import mock

from metrics.api import context_processors

MODULE_PATH: str = "metrics.api.context_processors"


@mock.patch(f"{MODULE_PATH}.config")
def test_frontend_url(spy_config: mock.MagicMock):
    """
    Given a mocked request
    When `frontend_url()` is called from the
        `context_processors` module
    Then a dict is returned with the `FRONTEND_URL` env variable
    """
    # Given
    mocked_request = mock.Mock()

    # When
    returned_url: Dict[str, str] = context_processors.frontend_url(
        request=mocked_request
    )

    # Then
    assert returned_url["frontend_url"] == spy_config.FRONTEND_URL
