from typing import Any

from rest_framework_api_key.crypto import concatenate
from rest_framework_api_key.models import APIKey, APIKeyManager


class CustomAPIKeyManager(APIKeyManager):
    """This custom model manager for the `APIKey` provides extra logic to handle pre-generated passwords.

    Note that this model manager is not initialized and set on the `objects` attribute of the `APIKey`
    or any subclasses of the `APIKey`.

    This is because the models created are still to be persisted with to the original
    `rest_framework_api_key_apikey` table instead of a new subclassed table.

    Given that the schema of the data being persisted remains the same.
    The only thing being customized is the creation logic,
    specifically around whether to create passwords or accept them from some input.

    As such, a new table was not needed.

    """

    def create_key(self, **kwargs: Any) -> tuple[APIKey, str]:
        """Creates an `APIKey` object and sets it up with the `api_key`, if given.

        If the `api_key` is not provided, then the fallback `create_key` method will be used.

        Returns:
            Tuple containing:
                1. The `APIKey` object itself
                2. The computed key with a plain prefix
                    and a hashed version of the suffix,
                    delimited by a single `.` character
            Examples:
                >>> "ag619m16.pbkdf2_sha256$390000$TXIvqYpKSbCjtmiOAijmwj$d/0E36V5W5Ng4KRSIYyuOrBRhWVSaBY52LlNMWOJDls="

        """
        try:
            api_key: str = kwargs.pop("api_key")
        except KeyError:
            return super().create_key(**kwargs)

        password_prefix, password_suffix = api_key.split(".")

        return self.assign_pre_generated_key(
            password_prefix=password_prefix, password_suffix=password_suffix, **kwargs
        )

    def assign_pre_generated_key(
        self, password_prefix: str, password_suffix: str, **kwargs
    ) -> tuple[APIKey, str]:
        """Creates an `APIKey` object and sets it up with the given `password_prefix` and `password_suffix`.

        Args:
            `password_prefix`: The pre-generated prefix.
                This should be an 8-character string
            `password_suffix`: The pre-generated suffix.
                This should be a 32-character string

        Returns:
            Tuple containing:
                1. The `APIKey` object itself
                2. The computed key with the original `password_prefix`
                and the hashed version of the `password_suffix`.
                These 2 parts of the key will be delimited by a `.` character
            Examples:
                assign_pre_generated_key(password_prefix="ag619m16", password_suffix=...)
                >>> "ag619m16.pbkdf2_sha256$390000$TXIvqYpKSbCjtmiOAijmwj$d/0E36V5W5Ng4KRSIYyuOrBRhWVSaBY52LlNMWOJDls="

        """
        kwargs.pop("id", None)
        key_obj = APIKey(**kwargs)

        key: str = self.set_pre_generated_password_on_key(
            key_obj=key_obj,
            password_prefix=password_prefix,
            password_suffix=password_suffix,
        )

        key_obj.save()

        return key_obj, key

    def set_pre_generated_password_on_key(
        self, key_obj, password_prefix: str, password_suffix: str
    ) -> str:
        """Set the hashed key in the format expected with the given `password_prefix` and `password_suffix`

        Args:
            `key_obj`: The created `APIKey` object which will be used to
                persist the pre-generated key information
            `password_prefix`: The pre-generated prefix.
                This should be an 8-character string
            `password_suffix`: The pre-generated suffix.
                This should be a 32-character string

        Returns:
            str: The computed key with the original `password_prefix`
                and the hashed version of the `password_suffix`.
                These 2 parts of the key will be delimited by a `.` character
            Examples:
                create_pre_generated_key(..., password_prefix="ag619m16", password_suffix=...)
                >>> "ag619m16.pbkdf2_sha256$390000$TXIvqYpKSbCjtmiOAijmwj$d/0E36V5W5Ng4KRSIYyuOrBRhWVSaBY52LlNMWOJDls="
        """

        full_plain_key: str = concatenate(left=password_prefix, right=password_suffix)
        hashed_key: str = self.key_generator.hash(value=full_plain_key)

        key: str = concatenate(left=password_prefix, right=hashed_key)

        key_obj.id = key
        key_obj.prefix = password_prefix
        key_obj.hashed_key = hashed_key

        return key
