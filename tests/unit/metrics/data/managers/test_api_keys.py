from typing import Dict
from unittest import mock

import pytest
from rest_framework_api_key.models import APIKeyManager

from metrics.data.managers.api_keys import CustomAPIKeyManager


class TestCustomAPIKeyManager:
    @property
    def fake_password_prefix(self) -> str:
        return "ag619m16"

    @property
    def fake_password_suffix(self) -> str:
        return "16ui27iu26ui236827io26897yvbn19d"

    @mock.patch.object(CustomAPIKeyManager, "assign_pre_generated_key")
    @mock.patch.object(APIKeyManager, "create_key")
    @pytest.mark.parametrize(
        "kwargs_for_create_key",
        [
            {"password_prefix": "12345678", "name": "fake_name"},
            {"password_suffix": "12345678910123456789", "name": "fake_name"},
            {"name": "fake_name"},
        ],
    )
    def test_create_key_falls_back_to_super_method_if_no_password_is_provided(
        self,
        spy_create_key_from_parent_class: mock.MagicMock,
        spy_assign_pre_generated_key: mock.MagicMock,
        kwargs_for_create_key: Dict[str, str],
    ):
        """
        Given a set of kwargs which do not contain both a password prefix and suffix
        When `create_key()` is called from an instance of the `CustomAPIKeyManager`
        Then the call is delegated to the `super().create_key()` method
        """
        # Given
        api_key_manager = CustomAPIKeyManager()

        # When
        key = api_key_manager.create_key(**kwargs_for_create_key)

        # Then
        # Check that the super `create_key` method is called and delegated to instead
        # And that any incomplete portion of the given password is not passed through
        spy_create_key_from_parent_class.assert_called_once_with(name="fake_name")
        assert key == spy_create_key_from_parent_class.return_value

        # Check that the `assign_pre_generated_key()` method is not called
        spy_assign_pre_generated_key.assert_not_called()

    @mock.patch.object(CustomAPIKeyManager, "assign_pre_generated_key")
    @mock.patch.object(APIKeyManager, "create_key")
    def test_create_key_delegates_to_assign_pre_generated_key_if_password_provided(
        self,
        spy_create_key_from_parent_class: mock.MagicMock,
        spy_assign_pre_generated_key: mock.MagicMock,
    ):
        """
        Given a password prefix and suffix
        When `create_key()` is called from an instance of the `CustomAPIKeyManager`
        Then the call is delegated to the `assign_pre_generated_key()` method
        """
        # Given
        api_key_manager = CustomAPIKeyManager()
        fake_name = "fake_name_for_api_key"
        password_prefix = self.fake_password_prefix
        password_suffix = self.fake_password_suffix

        # When
        key = api_key_manager.create_key(
            name=fake_name,
            password_prefix=password_prefix,
            password_suffix=password_suffix,
        )

        # Then
        # Check that the super `create_key` method is not called
        spy_create_key_from_parent_class.assert_not_called()

        # Check that the `assign_pre_generated_key()` method is delegated to
        # And the given password prefix and suffixes are passed into it
        spy_assign_pre_generated_key.assert_called_once_with(
            name=fake_name,
            password_prefix=password_prefix,
            password_suffix=password_suffix,
        )
        assert key == spy_assign_pre_generated_key.return_value

    @mock.patch.object(CustomAPIKeyManager, "set_pre_generated_password_on_key")
    def test_assign_pre_generated_key_initializes_model_with_correct_args(
        self, mocked_set_pre_generated_password_on_key: mock.MagicMock
    ):
        """
        Given a set of arguments
        When `assign_pre_generated_key()` is called from an instance of the `CustomAPIKeyManager`
        Then the model instance is initialized with the correct args

        Patches:
            `mocked_set_pre_generated_password_on_key`: To remove
                long-running side effects of creating hashes.
                This takes roughly 100ms.
                Hence, why it has been patched out of the test.
        """
        # Given
        name = "fake_name"
        fake_id = "fake_id"
        spy_model = mock.Mock()

        api_key_manager = CustomAPIKeyManager()
        api_key_manager.model = spy_model

        # When
        key_obj, _ = api_key_manager.assign_pre_generated_key(
            password_prefix=self.fake_password_prefix,
            password_suffix=self.fake_password_suffix,
            name=name,
            id=fake_id,
        )

        # Then
        # Check that `model` is called with the correct kwargs
        # this should exclude id, and the password kwargs
        spy_model.assert_called_once_with(name=name)
        assert key_obj == spy_model.return_value

    @mock.patch.object(CustomAPIKeyManager, "set_pre_generated_password_on_key")
    def test_assign_pre_generated_key_saves_and_returns_model_instance_and_key(
        self, spy_set_pre_generated_password_on_key: mock.MagicMock
    ):
        """
        Given a set of arguments
        When `assign_pre_generated_key()` is called from an instance of the `CustomAPIKeyManager`
        Then the model instance is saved and returned
        And the key is also returned from the `set_pre_generated_password_on_key()` method
        """
        # Given
        spy_model = mock.Mock()

        api_key_manager = CustomAPIKeyManager()
        api_key_manager.model = spy_model

        # When
        key_obj, key = api_key_manager.assign_pre_generated_key(
            password_prefix=self.fake_password_prefix,
            password_suffix=self.fake_password_suffix,
        )

        # Then
        expected_returned_key_obj = spy_model.return_value
        expected_returned_key_obj.save.assert_called_once()
        assert key_obj == expected_returned_key_obj
        assert key == spy_set_pre_generated_password_on_key.return_value

    @mock.patch.object(CustomAPIKeyManager, "key_generator")
    def test_set_pre_generated_password_on_key_sets_prefix_on_key(
        self, mocked_key_generator: mock.MagicMock
    ):
        """
        Given an 8-length password prefix and 32-length suffix
        And a mock in place of the `APIKey` object
        When `set_pre_generated_password_on_key()` is called
            from an instance of the `CustomAPIKeyManager`
        Then the `prefix` is set on the key object

        Patches:
            `key_generator`: To remove long-running side effects
                of creating hashes. This takes roughly 100ms.
                Hence, why it has been patched out of the test.
        """
        # Given
        mocked_key_obj = mock.Mock()
        api_key_manager = CustomAPIKeyManager()

        # When
        api_key_manager.set_pre_generated_password_on_key(
            key_obj=mocked_key_obj,
            password_prefix=self.fake_password_prefix,
            password_suffix=self.fake_password_suffix,
        )

        # Then
        assert mocked_key_obj.prefix == self.fake_password_prefix

    @mock.patch.object(CustomAPIKeyManager, "key_generator")
    def test_set_pre_generated_password_on_key_delegates_hashing_of_key_correctly(
        self, spy_key_generator: mock.MagicMock
    ):
        """
        Given an 8-length password prefix and 32-length suffix
        And a mock in place of the `APIKey` object
        When `set_pre_generated_password_on_key()` is called
            from an instance of the `CustomAPIKeyManager`
        Then the `prefix` is set on the key object
        """
        # Given
        mocked_key_obj = mock.Mock()
        api_key_manager = CustomAPIKeyManager()

        # When
        key = api_key_manager.set_pre_generated_password_on_key(
            key_obj=mocked_key_obj,
            password_prefix=self.fake_password_prefix,
            password_suffix=self.fake_password_suffix,
        )

        # Then
        # Check that the key generator is used to hash the full plain key
        # Whereby the full plain key splits the prefix and suffix by a `.` character
        expected_full_plain_key = (
            f"{self.fake_password_prefix}.{self.fake_password_suffix}"
        )
        spy_key_generator.hash.assert_called_once_with(value=expected_full_plain_key)

        # Check that the key is the original prefix and the hashed suffix.
        # This should also be splits by a `.` character
        mocked_hashed_key = spy_key_generator.hash.return_value
        expected_hashed_key = f"{self.fake_password_prefix}.{mocked_hashed_key}"
        # This should also be set as the `id` of the key object
        assert mocked_key_obj.id == key == expected_hashed_key

        # Check that the `hashed_key` is set only to the hashed password suffix
        assert mocked_key_obj.hashed_key == mocked_hashed_key
