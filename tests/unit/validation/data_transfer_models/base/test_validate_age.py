import pytest
from pydantic_core._pydantic_core import ValidationError

from validation.data_transfer_models.base import IncomingBaseDataModel


class TestIncomingBaseValidationForAge:
    def test_all_value_is_deemed_valid(
        self, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a valid age value of the string "all"
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = "all"

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "age",
        (
            "65-69",
            "70-74",
            "75-79",
            "15-19",
            "55-59",
            "85-89",
            "35-39",
            "00-04",
            "45-64",
            "80-84",
            "25-29",
            "20-24",
            "65-74",
        ),
    )
    def test_age_band_value_is_deemed_valid(
        self, age: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a valid age value of an age banding
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = age

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "age",
        (
            "65+",
            "80+",
            "85+",
            "75+",
            "50+",
            "90+",
        ),
    )
    def test_age_older_than_value_is_deemed_valid(
        self, age: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a valid age value which is older than a particular age
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = age

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "age",
        (
            "69-65",
            "74-70",
            "79-75",
            "19-15",
            "59-55",
            "89-85",
            "39-35",
            "04-00",
            "64-45",
            "84-80",
            "29-25",
            "24-20",
            "74-65",
        ),
    )
    def test_older_than_age_bandings_with_lower_number_on_the_right_side_throws_error(
        self, age: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given an age banding value whereby
            the lower number is on the right side
            i.e. `19-15` instead of `15-19`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidatorError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = age

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "age",
        (
            "0-4",
            "00-4",
            "0-04",
            "5-14",
        ),
    )
    def test_age_bandings_with_single_digit_numbers_throws_error(
        self, age: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given an age banding with at least one single digit number
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = age

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "age",
        (
            "ALL",
            "default",
            "Default",
            "any",
        ),
    )
    def test_age_strings_with_incorrect_value_throws_error(
        self, age: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given an age alphabetic value
            which is not the literal string "all"
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = age

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "age",
        (
            "85-",
            "+85",
            "00,04",
            "-0400",
            "00_04",
            "0_4",
            "00+04",
            "00±04",
            "8o+",
            "oo-04",
        ),
    )
    def test_age_value_with_incorrect_operator_throws_error(
        self, age: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given an age value with an invalid operator
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["age"] = age

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
