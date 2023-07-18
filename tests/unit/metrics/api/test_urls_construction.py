import pytest
from django.urls.resolvers import URLResolver

from metrics.api.urls_construction import construct_urlpatterns
from public_api.urls import PUBLIC_API_PREFIX

HEADLESS_CMS_API_ENDPOINT_PATHS = ["drafts", "pages"]

PRIVATE_API_ENDPOINT_PATHS = [
    "api/charts/v2",
    "api/charts/v3",
    "api/downloads/v2",
    "api/headlines/v2",
    "api/tables/v2",
    "api/trends/v2",
    "api/suggestions/v1",
]


PUBLIC_API_ENDPOINT_PATHS = [f"{PUBLIC_API_PREFIX}", f"{PUBLIC_API_PREFIX}themes"]

CMS_ADMIN_ENDPOINT_PATHS = ["cms", "admin"]

COMMON_ENDPOINT_PATHS = [
    "api/schema",
    "api/swagger",
    "api/redoc",
    "static",
    "health",
]


class TestConstructUrlpatterns:
    # Tests for APP_MODE = "PRIVATE_API"

    @pytest.mark.parametrize("private_api_endpoint_path", PRIVATE_API_ENDPOINT_PATHS)
    def test_private_api_mode_returns_private_api_urls(
        self, private_api_endpoint_path: str
    ):
        """
        Given an `app_mode` of "PRIVATE_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the private API endpoints
        """
        # Given
        app_mode = "PRIVATE_API"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any(
            private_api_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
        )

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
        app_mode = "PRIVATE_API"

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
        "excluded_endpoint_path", PUBLIC_API_ENDPOINT_PATHS + CMS_ADMIN_ENDPOINT_PATHS
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
        app_mode = "PRIVATE_API"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(
            excluded_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
        )

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
        app_mode = "PUBLIC_API"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any(
            public_api_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
        )

    @pytest.mark.parametrize(
        "excluded_endpoint_path", PRIVATE_API_ENDPOINT_PATHS + CMS_ADMIN_ENDPOINT_PATHS
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
        app_mode = "PUBLIC_API"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(
            excluded_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
        )

    # Tests for APP_MODE = "CMS_ADMIN"

    @pytest.mark.parametrize("cms_admin_endpoint_path", CMS_ADMIN_ENDPOINT_PATHS)
    def test_cms_admin_mode_returns_cms_admin_urls(self, cms_admin_endpoint_path: str):
        """
        Given an `app_mode` of "CMS_ADMIN"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the CMS admin endpoints
        """
        # Given
        app_mode = "CMS_ADMIN"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any(
            cms_admin_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
        )

    @pytest.mark.parametrize(
        "excluded_endpoint_path", PRIVATE_API_ENDPOINT_PATHS + PUBLIC_API_ENDPOINT_PATHS
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
        app_mode = "CMS_ADMIN"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert not any(
            excluded_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
        )

    # Tests for common/shared endpoints

    @pytest.mark.parametrize(
        "endpoint_path",
        PRIVATE_API_ENDPOINT_PATHS
        + PUBLIC_API_ENDPOINT_PATHS
        + CMS_ADMIN_ENDPOINT_PATHS,
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
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        assert any(endpoint_path in x.pattern.regex.pattern for x in urlpatterns)

    @pytest.mark.parametrize(
        "app_mode",
        [
            "CMS_ADMIN",
            "PUBLIC_API",
            "PRIVATE_API",
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
        assert any(common_endpoint_path in x.pattern.regex.pattern for x in urlpatterns)
