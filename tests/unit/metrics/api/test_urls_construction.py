from unittest import mock

import pytest
from django.urls.resolvers import URLResolver, URLPattern

from metrics.api import enums
from metrics.api.urls_construction import (
    DEFAULT_PUBLIC_API_PREFIX,
    construct_cms_admin_urlpatterns,
    construct_public_api_urlpatterns,
    construct_urlpatterns,
)
from public_api.metrics_interface.interface import MetricsPublicAPIInterface

MODULE_PATH = "metrics.api.urls_construction"

HEADLESS_CMS_API_ENDPOINT_PATHS = ["drafts", "pages"]

PRIVATE_API_ENDPOINT_PATHS = [
    "api/downloads/v2",
    "api/headlines/v3",
    "api/bulkdownloads/v1",
    "api/tables/v4",
    "api/trends/v3",
    "api/geographies/v2/",
]

AUDIT_API_ENDPOINT_PATHS = [
    "api/audit/v1/api-timeseries",
    "api/audit/v1/core-timeseries",
    "api/audit/v1/core-headline",
    "api/charts/v2",
]

FEEDBACK_API_ENDPOINT_PATHS = ["api/suggestions/v2"]

PUBLIC_API_ENDPOINT_PATHS = [
    "themes/<str:theme>/",
    "sub_themes/<str:sub_theme>/",
    "topics/<str:topic>/",
    "geography_types/<str:geography_type>/",
    "geographies/<str:geography>/",
    "metrics/<str:metric>",
]

CMS_ADMIN_ENDPOINT_PATHS = ["cms", "admin"]

COMMON_ENDPOINT_PATHS = [
    "api/schema",
    "api/swagger",
    "api/redoc",
    "static",
    "health",
]

VERSIONED_APP_NAMES = [
    "public_api",
]


def _flatten_urls(*, urlpatterns: list[URLPattern | URLResolver]) -> list[URLPattern]:
    """Takes a list of URLPatterns and URLResolvers and returns
        a list where each URLPattern belonging to a URLResolver
        from a `versioned` set of URLs has been added to the top
        level of the list.

    Args:
        urlpatterns: list[URLPattern, URLResolver]

    Returns:
        list[URLPattern
    """
    flattened_urls = []
    for item in urlpatterns:
        if type(item) == URLResolver and item.app_name in VERSIONED_APP_NAMES:
            flattened_urls.extend(item.url_patterns)
        else:
            flattened_urls.append(item)

    return flattened_urls


class TestConstructCMSAdminUrlpatterns:
    def test_app_mode_cms_admin_returns_at_root(self):
        """
        Given an `app_mode` of "CMS_ADMIN"
        When `construct_cms_admin_urlpatterns()` is called
        Then the urlpatterns returned sets the cms admin URL at the root
        """
        # Given
        app_mode = enums.AppMode.CMS_ADMIN.value

        # When
        urlpatterns = construct_cms_admin_urlpatterns(app_mode=app_mode)

        # Then
        cms_admin_url_resolver: URLResolver = urlpatterns[0]
        assert cms_admin_url_resolver.pattern.regex.pattern == "^"

    @pytest.mark.parametrize(
        "app_mode",
        [
            None,
            "",
            "COMPLETE_APP",
        ],
    )
    def test_no_specific_app_mode_returns_at_designated_path(
        self, app_mode: str | None
    ):
        """
        Given any default `app_mode` value
        When `construct_cms_admin_urlpatterns()` is called
        Then the urlpatterns returned sets the cms admin URL at "/cms-admin/
        """
        # Given
        provided_app_mode = app_mode

        # When
        urlpatterns = construct_cms_admin_urlpatterns(app_mode=provided_app_mode)

        # Then
        cms_admin_url_resolver: URLResolver = urlpatterns[0]
        assert cms_admin_url_resolver.pattern.regex.pattern == "^cms\\-admin/"


class TestConstructPublicAPIUrlpatterns:
    @mock.patch(f"{MODULE_PATH}.construct_url_patterns_for_public_api")
    def test_public_api_app_mode_uses_root_as_prefix(
        self, spy_construct_url_patterns_for_public_api: mock.MagicMock
    ):
        """
        Given an `app_mode` of "PUBLIC_API"
        When `construct_public_api_urlpatterns()` is called
        Then the root url is passed to the call
            to `construct_urlpatterns_for_public_api()
        """
        # Given
        app_mode = enums.AppMode.PUBLIC_API.value

        # When
        urlpatterns = construct_public_api_urlpatterns(app_mode=app_mode)

        # Then
        spy_construct_url_patterns_for_public_api.assert_called_once_with(prefix="")
        assert urlpatterns == spy_construct_url_patterns_for_public_api.return_value

    @pytest.mark.parametrize(
        "app_mode",
        [
            None,
            "",
            "COMPLETE_APP",
        ],
    )
    @mock.patch(f"{MODULE_PATH}.construct_url_patterns_for_public_api")
    def test_public_api_app_mode_returns_at_designated_path(
        self,
        spy_construct_url_patterns_for_public_api: mock.MagicMock,
        app_mode: str | None,
    ):
        """
        Given any default `app_mode` value
        When `construct_public_api_urlpatterns()` is called
        Then the root url is passed to the call
            to `construct_urlpatterns_for_public_api()
        """
        # Given
        provided_app_mode = app_mode

        # When
        urlpatterns = construct_public_api_urlpatterns(app_mode=provided_app_mode)

        # Then
        spy_construct_url_patterns_for_public_api.assert_called_once_with(
            prefix=DEFAULT_PUBLIC_API_PREFIX
        )
        assert urlpatterns == spy_construct_url_patterns_for_public_api.return_value


class TestConstructUrlpatterns:
    # Tests for APP_MODE = "PRIVATE_API"

    @pytest.mark.parametrize(
        "private_api_endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS,
    )
    def test_private_api_mode_returns_private_api_urls(
        self, private_api_endpoint_path: str
    ):
        """
        Given an `app_mode` of "PRIVATE_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the private API endpoints
        """
        # Given
        app_mode = enums.AppMode.PRIVATE_API.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any(private_api_endpoint_path in str(x.pattern) for x in urlpatterns)

    @pytest.mark.parametrize(
        "headless_cms_api_endpoint_path", HEADLESS_CMS_API_ENDPOINT_PATHS
    )
    def test_private_api_mode_returns_headless_cms_api_urls(
        self, headless_cms_api_endpoint_path: str
    ):
        """
        Given an `app_mode` of "PRIVATE_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the headless CMS pages endpoints
        """
        # Given
        app_mode = enums.AppMode.PRIVATE_API.value

        # When
        private_api_urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        cms_url_resolver = next(
            x
            for x in private_api_urlpatterns
            if getattr(x, "app_name", None) == "wagtailapi"
        )
        namespaces: dict[str, tuple[str, URLResolver]] = cms_url_resolver.namespace_dict
        assert headless_cms_api_endpoint_path in namespaces

    @pytest.mark.parametrize(
        "excluded_endpoint_path",
        PUBLIC_API_ENDPOINT_PATHS
        + CMS_ADMIN_ENDPOINT_PATHS
        + FEEDBACK_API_ENDPOINT_PATHS
        + AUDIT_API_ENDPOINT_PATHS,
    )
    def test_private_api_mode_does_not_return_other_urls(
        self, excluded_endpoint_path: str
    ):
        """
        Given an `app_mode` of "PRIVATE_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = enums.AppMode.PRIVATE_API.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(excluded_endpoint_path in str(x.pattern) for x in urlpatterns)

    # Tests for APP_MODE = "PUBLIC_API"

    @pytest.mark.parametrize("public_api_endpoint_path", PUBLIC_API_ENDPOINT_PATHS)
    def test_public_api_mode_returns_public_api_urls(
        self, public_api_endpoint_path: str
    ):
        """
        Given an `app_mode` of "PUBLIC_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the public API endpoints
        """
        # Given
        app_mode = enums.AppMode.PUBLIC_API.value

        # When
        flattened_urls = _flatten_urls(
            urlpatterns=construct_urlpatterns(app_mode=app_mode)
        )

        # Then
        assert any(public_api_endpoint_path in str(x.pattern) for x in flattened_urls)

    @pytest.mark.parametrize(
        "excluded_endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS
        + CMS_ADMIN_ENDPOINT_PATHS
        + FEEDBACK_API_ENDPOINT_PATHS
        + AUDIT_API_ENDPOINT_PATHS,
    )
    def test_public_api_mode_does_not_return_other_urls(
        self, excluded_endpoint_path: str
    ):
        """
        Given an `app_mode` of "PUBLIC_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = enums.AppMode.PUBLIC_API.value

        # When
        flattened_urls = _flatten_urls(
            urlpatterns=construct_urlpatterns(app_mode=app_mode)
        )

        # Then
        assert not any(excluded_endpoint_path in str(x.pattern) for x in flattened_urls)

    def test_public_api_with_auth_enabled_includes_robots_txt_url(self):
        """
        Given `AUTH_ENABLED` is set to True
        And an `app_mode` of "PUBLIC_API"
        When `construct_urlpatterns()` is called
        Then the returned urls patterns
            does contain `robots.txt`
        """
        # Given
        app_mode = enums.AppMode.PUBLIC_API.value

        # When
        with mock.patch.object(
            MetricsPublicAPIInterface,
            "is_auth_enabled",
            return_value=True,
        ):
            flattened_urls = _flatten_urls(
                urlpatterns=construct_urlpatterns(app_mode=app_mode)
            )

        # Then
        patterns = [str(x.pattern) for x in flattened_urls]
        assert "robots.txt" in patterns

    def test_public_api_with_auth_disabled_excludes_robots_txt_url(self):
        """
        Given `AUTH_ENABLED` is set to False
        And an `app_mode` of "PUBLIC_API"
        When `construct_urlpatterns()` is called
        Then the returned urls patterns
            do not contain `robots.txt`
        """
        # Given
        app_mode = enums.AppMode.PUBLIC_API.value

        # When
        with mock.patch.object(
            MetricsPublicAPIInterface,
            "is_auth_enabled",
            return_value=False,
        ):
            flattened_urls = _flatten_urls(
                urlpatterns=construct_urlpatterns(app_mode=app_mode)
            )

        # Then
        patterns = [str(x.pattern) for x in flattened_urls]
        assert "robots.txt" not in patterns

    # Tests for APP_MODE = "CMS_ADMIN"

    def test_cms_admin_mode_returns_cms_admin_urls(self):
        """
        Given an `app_mode` of "CMS_ADMIN"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the CMS admin endpoints
        """
        # Given
        app_mode = enums.AppMode.CMS_ADMIN.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any("admin" in str(x.pattern) for x in urlpatterns)

    @pytest.mark.parametrize(
        "included_endpoint_path",
        AUDIT_API_ENDPOINT_PATHS,
    )
    def test_cms_admin_mode_returns_all_expected_urls(
        self, included_endpoint_path: str
    ):
        """
        Given an `app_mode` of "CMS_ADMIN"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the audit api endpoints
        """
        # Given
        app_mode = enums.AppMode.CMS_ADMIN.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any(included_endpoint_path in str(x.pattern) for x in urlpatterns)

    @pytest.mark.parametrize(
        "excluded_endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS
        + PUBLIC_API_ENDPOINT_PATHS
        + FEEDBACK_API_ENDPOINT_PATHS,
    )
    def test_cms_admin_mode_does_not_return_other_urls(
        self, excluded_endpoint_path: str
    ):
        """
        Given an `app_mode` of "CMS_ADMIN"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = enums.AppMode.CMS_ADMIN.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(excluded_endpoint_path in str(x.pattern) for x in urlpatterns)

    # Tests for APP_MODE = "FEEDBACK_API"

    def test_feedback_api_mode_returns_feedback_api_urls(self):
        """
        Given an `app_mode` of "FEEDBACK_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the feedback API endpoints
        """
        # Given
        app_mode = enums.AppMode.FEEDBACK_API.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any("suggestions" in str(x.pattern) for x in urlpatterns)

    @pytest.mark.parametrize(
        "excluded_endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS
        + PUBLIC_API_ENDPOINT_PATHS
        + CMS_ADMIN_ENDPOINT_PATHS,
    )
    def test_feedback_api_mode_does_not_return_other_urls(
        self, excluded_endpoint_path: str
    ):
        """
        Given an `app_mode` of "FEEDBACK_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = enums.AppMode.FEEDBACK_API.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(excluded_endpoint_path in str(x.pattern) for x in urlpatterns)

    # Tests for APP_MODE = "INGESTION"

    @pytest.mark.parametrize(
        "excluded_endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS
        + PUBLIC_API_ENDPOINT_PATHS
        + FEEDBACK_API_ENDPOINT_PATHS
        + CMS_ADMIN_ENDPOINT_PATHS,
    )
    def test_ingestion_mode_does_not_return_other_urls(
        self, excluded_endpoint_path: str
    ):
        """
        Given an `app_mode` of "INGESTION"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = enums.AppMode.INGESTION.value

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(excluded_endpoint_path in str(x.pattern) for x in urlpatterns)

    # Tests for common/shared endpoints
    @pytest.mark.parametrize(
        "endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS
        + PUBLIC_API_ENDPOINT_PATHS
        + CMS_ADMIN_ENDPOINT_PATHS
        + FEEDBACK_API_ENDPOINT_PATHS
        + AUDIT_API_ENDPOINT_PATHS,
    )
    def test_no_specific_app_mode_returns_all_urls(self, endpoint_path: str):
        """
        Given no value given for the `app_mode`
        When `construct_urlpatterns()` is called
        Then all the urlpatterns are returned
        """
        # Given
        app_mode = None

        # When
        flattened_urls = _flatten_urls(
            urlpatterns=construct_urlpatterns(app_mode=app_mode)
        )

        # Then
        assert any(endpoint_path in str(x.pattern) for x in flattened_urls)

    @pytest.mark.parametrize(
        "app_mode",
        [
            enums.AppMode.CMS_ADMIN.value,
            enums.AppMode.PUBLIC_API.value,
            enums.AppMode.PRIVATE_API.value,
            enums.AppMode.FEEDBACK_API.value,
            enums.AppMode.INGESTION.value,
            None,
            "",
            "COMPLETE_APP",
        ],
    )
    @pytest.mark.parametrize("common_endpoint_path", COMMON_ENDPOINT_PATHS)
    def test_base_set_of_urls_returned_regardless_of_app_mode(
        self, app_mode: str, common_endpoint_path: str
    ):
        """
        Given any `app_mode` value
        When `construct_urlpatterns()` is called
        Then the common shared endpoints are returned
            regardless of the `app_mode` input
        """
        # Given
        provided_app_mode: str = app_mode

        # When
        urlpatterns = construct_urlpatterns(app_mode=provided_app_mode)

        # Then
        assert any(common_endpoint_path in str(x.pattern) for x in urlpatterns)
