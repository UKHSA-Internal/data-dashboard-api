from integrations import frontend


class TestAPIClient:
    def test_revalidate_url_has_correct_path(self):
        """
        Given
        When
        Then
        """
        # Given
        fake_url = "fake-url.com"
        fake_key = "some-fake-key"

        api_client = frontend.APIClient(url=fake_url, key=fake_key)

        # When
        revalidate_url: str = api_client.revalidate_url

        # Then
        assert revalidate_url == f"{fake_url}/api/revalidate"

    def test_get_request_passes_key_to_params_of_request(self):
        """
        Given
        When
        Then
        """
        # Given
        fake_url = "fake-url.com"
        fake_key = "some-fake-key"

        api_client = frontend.APIClient(url=fake_url, key=fake_key)

        # When
        revalidate_url: str = api_client.revalidate_url

        # Then
        assert revalidate_url == f"{fake_url}/api/revalidate"


