from unittest import mock

from integrations import frontend

MODULE_PATH = "integrations.frontend"


class TestAPIClient:
    def test_revalidate_url_has_correct_path(self):
        """
        Given a base URL
        When the `revalidate_url` property is called from an instance of the `APIClient`
        Then the correct URL for the `revalidate` endpoint is returned
        """
        # Given
        fake_url = "https://fake-url.com"
        api_key = "some-fake-key"
        api_client = frontend.APIClient(base_url=fake_url, api_key=api_key)

        # When
        revalidate_url: str = api_client.revalidate_url

        # Then
        assert revalidate_url == f"{fake_url}/api/revalidate"

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_get_request_passes_key_to_params_of_request(
        self, requests_spy: mock.MagicMock
    ):
        """
        Given a base URL and an API key
        When the `_get_request` property is called from an instance of the `APIClient`
        Then the `get` is called from the `requests` library with the correct args,
            including the API key
        """
        # Given
        fake_url = "https://fake-url.com"
        api_key = "some-fake-key"
        api_client = frontend.APIClient(base_url=fake_url, api_key=api_key)

        # When
        response = api_client._get_request(url=fake_url)

        # Then
        expected_params = {"secret": api_key}
        requests_spy.get.assert_called_once_with(
            url=fake_url,
            params=expected_params,
        )
        assert response == requests_spy.get.return_value

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_send_request_to_revalidate_page(self, requests_spy: mock.MagicMock):
        """
        Given a base URL and a slug, which is an identifier for a specific page
        When the `send_request_to_revalidate_page()` is called from an instance of the `APIClient`
        Then the `get` is called from the `requests` library with the correct args.
        """
        # Given
        fake_url = "https://fake-url.com"
        api_key = "some-fake-key"
        slug = "influenza"
        api_client = frontend.APIClient(base_url=fake_url, api_key=api_key)

        # When
        response = api_client.send_request_to_revalidate_page(slug=slug)

        # Then
        expected_params = {"secret": api_key, "slug": slug}
        expected_url = f"{fake_url}/api/revalidate"

        requests_spy.get.assert_called_once_with(
            url=expected_url,
            params=expected_params,
        )
        assert response == requests_spy.get.return_value
