from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from cms.snippets.models.global_banner import BannerTypes
from tests.factories.cms.snippets.global_banner import GlobalBannerFactory


class TestGlobalBannerView:
    @property
    def path(self) -> str:
        return "/api/global-banners/v1"

    @pytest.mark.django_db
    def test_get_request_returns_correct_data(self):
        """
        Given an active `GlobalBanner` record
        When a GET request is made to the `/api/global-banners/v1` endpoint
        Then the response is a valid HTTP OK with the correct data
        """
        # Given
        client = APIClient()
        active_banner_info = {
            "title": "this is the active banner title",
            "body": "this is the active banner body",
            "banner_type": BannerTypes.WARNING.value,
            "is_active": True,
        }
        active_global_banner = GlobalBannerFactory.create(**active_banner_info)

        # When
        response: Response = client.get(
            path=self.path,
            format="json",
            headers={"CACHE_FORCE_REFRESH_HEADER_KEY": True},
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert (
            response.data["active_global_banner"]["title"] == active_global_banner.title
        )
        assert (
            response.data["active_global_banner"]["body"] == active_global_banner.body
        )
        assert (
            response.data["active_global_banner"]["banner_type"]
            == active_global_banner.banner_type
        )
