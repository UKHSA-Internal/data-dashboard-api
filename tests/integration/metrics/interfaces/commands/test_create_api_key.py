import pytest
from django.core.management import call_command
from rest_framework_api_key.models import APIKey


class TestCreateAPIKey:
    @pytest.mark.django_db
    def test_command_creates_api_key_with_provided_password(
        self,
        fake_password_prefix: str,
        fake_password_suffix: str,
    ):
        """
        Given a `password_prefix` and a `password_suffix`
        When the `create_api_key` management command is called
        Then an `APIKey` is created with the provided password components
        """
        # Given
        password_prefix = fake_password_prefix
        password_suffix = fake_password_suffix

        assert not APIKey.objects.all().exists()

        # When
        call_command(
            "create_api_key",
            password_prefix=password_prefix,
            password_suffix=password_suffix,
        )

        # Then
        # Check that the API key is created in the database
        assert APIKey.objects.all().exists()
        created_api_key: APIKey = APIKey.objects.last()
        assert created_api_key.prefix == fake_password_prefix

        expected_suffix, expected_hashed_key = created_api_key.id.split(".")

        assert expected_suffix == fake_password_prefix
        assert created_api_key.hashed_key == expected_hashed_key
