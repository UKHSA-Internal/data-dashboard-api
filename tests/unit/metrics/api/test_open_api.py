from unittest import mock

from metrics.api import open_api


def test_pre_processing_endpoint_filter_hook_for_cms_admin_endpoints():
    """
    Given a list of endpoints including one for the `cms-admin`
    When the `pre_processing_endpoint_filter_hook()` function is called
    Then the endpoint for the `cms-admin` is removed
    """
    # Given
    endpoints = [
        ("api/some/path", "xyz", "GET", mock.Mock()),
        ("api/another/path", "xyz", "GET", mock.Mock()),
        ("cms-admin/", "xyz", "GET", mock.Mock()),
    ]

    # When
    filtered_endpoints = open_api.pre_processing_endpoint_filter_hook(
        endpoints=endpoints
    )

    # Then
    assert len(filtered_endpoints) == 2
    assert "cms-admin" not in filtered_endpoints[0][0]
    assert "cms-admin" not in filtered_endpoints[1][0]


def test_pre_processing_endpoint_filter_hook_for_well_known_health_endpoint():
    """
    Given a list of endpoints including
        one for the `/.well-known/health-check/`
    When the `pre_processing_endpoint_filter_hook()` function is called
    Then the endpoint for the `/.well-known/health-check/` is removed
    """
    # Given
    endpoint_to_exclude = ".well-known/health-check/"

    endpoints = [
        ("api/some/path", "xyz", "GET", mock.Mock()),
        ("api/another/path", "xyz", "GET", mock.Mock()),
        (endpoint_to_exclude, "xyz", "GET", mock.Mock()),
    ]

    # When
    filtered_endpoints = open_api.pre_processing_endpoint_filter_hook(
        endpoints=endpoints
    )

    # Then
    assert len(filtered_endpoints) == 2
    assert endpoint_to_exclude not in filtered_endpoints[0][0]
    assert endpoint_to_exclude not in filtered_endpoints[1][0]
