from typing import Any, Tuple

from rest_framework_api_key.crypto import concatenate
from rest_framework_api_key.models import APIKeyManager


class CustomAPIKeyManager(APIKeyManager):
    def create_key(self, **kwargs: Any) -> Tuple["AbstractAPIKey", str]:
        """Creates an `APIKey` object and sets it up with the `password_prefix` and `password_suffix`, if given.

        If either `password_prefix` or `password_suffix` are not provided,
        then the fallback `create_key` method will be used.

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
            password_prefix = kwargs.pop("password_prefix")
            password_suffix = kwargs.pop("password_suffix")
        except KeyError:
            kwargs.pop("password_suffix", None)
            kwargs.pop("password_prefix", None)
            return super().create_key(**kwargs)

        return self.assign_pre_generated_key(
            password_prefix=password_prefix, password_suffix=password_suffix, **kwargs
        )

    def assign_pre_generated_key(
        self, password_prefix: str, password_suffix: str, **kwargs
    ) -> Tuple["AbstractAPIKey", str]:
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
        key_obj = self.model(**kwargs)

        key = self.set_pre_generated_password_on_key(
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
