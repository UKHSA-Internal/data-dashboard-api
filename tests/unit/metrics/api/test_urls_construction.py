import pytest
from django.urls.resolvers import URLResolver

from metrics.api.urls_construction import construct_urlpatterns
from public_api.urls import PUBLIC_API_PREFIX

HEADLESS_CMS_API_ENDPOINT_PATHS = ["drafts", "pages"]


class TestConstructUrlpatterns:
    @property
    def private_api_endpoint_paths(self) -> list[str]:
        api_prefix = "api"
        endpoints_paths = [
            "/charts/v2",
            "/downloads/v2",
            "/headlines/v2",
            "/tables/v2",
            "/trends/v2",
        ]
        deprecated_endpoints = endpoints_paths
        main_endpoints = [f"{api_prefix}{x}" for x in endpoints_paths]
        return main_endpoints + deprecated_endpoints

    @property
    def public_api_endpoint_paths(self) -> list[str]:
        return [f"{PUBLIC_API_PREFIX}", f"{PUBLIC_API_PREFIX}themes"]

    @property
    def cms_endpoint_paths(self) -> list[str]:
        return ["cms", "admin"]

    @property
    def common_endpoint_paths(self) -> list[str]:
        return [
            "api/schema",
            "api/swagger",
            "api/redoc",
            "static",
            "health",
        ]

    def test_private_api_mode_returns_private_api_urls(self):
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
        for private_api_endpoint_path in self.private_api_endpoint_paths:
            assert any(
                private_api_endpoint_path in x.pattern.regex.pattern
                for x in urlpatterns
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

    def test_private_api_mode_does_not_return_other_urls(self):
        """
        Given an `app_mode` of "PRIVATE_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = "PRIVATE_API"
        excluded_endpoint_paths: list[str] = (
            self.cms_endpoint_paths + self.public_api_endpoint_paths
        )

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        for excluded_endpoint_path in excluded_endpoint_paths:
            assert not any(
                excluded_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
            )

    def test_public_api_mode_returns_public_api_urls(self):
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
        for public_api_endpoint_path in self.public_api_endpoint_paths:
            assert any(
                public_api_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
            )

    def test_public_api_mode_does_not_return_other_urls(self):
        """
        Given an `app_mode` of "PUBLIC_API"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = "PUBLIC_API"
        excluded_endpoint_paths: list[str] = (
            self.private_api_endpoint_paths + self.cms_endpoint_paths
        )

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        for excluded_endpoint_path in excluded_endpoint_paths:
            assert not any(
                excluded_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
            )

    def test_cms_mode_returns_cms_urls(self):
        """
        Given an `app_mode` of "CMS"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned contain the CMS endpoints
        """
        # Given
        app_mode = "CMS"

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        for cms_endpoint_path in self.cms_endpoint_paths:
            assert any(
                cms_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
            )

    def test_cms_mode_does_not_return_other_urls(self):
        """
        Given an `app_mode` of "CMS"
        When `construct_urlpatterns()` is called
        Then the urlpatterns returned do not contain URLs for the other APIs
        """
        # Given
        app_mode = "CMS"
        excluded_endpoint_paths: list[str] = (
            self.private_api_endpoint_paths + self.public_api_endpoint_paths
        )

        # When
        urlpatterns = construct_urlpatterns(app_mode=app_mode)

        # Then
        for excluded_endpoint_path in excluded_endpoint_paths:
            assert not any(
                excluded_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
            )

    def test_no_specific_app_mode_returns_all_urls(self):
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
        all_endpoint_paths = (
            self.cms_endpoint_paths
            + self.public_api_endpoint_paths
            + self.private_api_endpoint_paths
        )
        for endpoint_path in all_endpoint_paths:
            assert any(endpoint_path in x.pattern.regex.pattern for x in urlpatterns)

    @pytest.mark.parametrize(
        "app_mode",
        [
            "CMS",
            "PUBLIC_API",
            "PRIVATE_API",
            None,
            "",
            "COMPLETE_APP",
        ],
    )
    def test_base_set_of_urls_returned_regardless_of_app_mode(self, app_mode: str):
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
        for common_endpoint_path in self.common_endpoint_paths:
            assert any(
                common_endpoint_path in x.pattern.regex.pattern for x in urlpatterns
            )
