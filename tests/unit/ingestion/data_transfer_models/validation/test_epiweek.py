import datetime

import pytest

from ingestion.data_transfer_models.validation.epiweek import validate_epiweek


class TestValidateEpiweek:
    @pytest.mark.parametrize(
        "input_epiweek, input_date",
        (
            [44, "2022-11-01"],
            [45, "2022-11-09"],
            [46, "2022-11-18"],
            [46, "2022-11-20"],
            [49, "2022-12-09"],
            [50, "2022-12-14"],
            [52, "2022-12-31"],
            [52, "2023-01-01"],
            [1, "2023-01-02"],
            [2, "2023-01-09"],
        ),
    )
    def test_validates_successfully(self, input_epiweek: int, input_date: str):
        """
        Given a valid pairing of epiweek and date
        When `validate_epiweek()` is called
        Then no error is raised
        """
        # Given
        epiweek = input_epiweek
        provided_date = datetime.datetime.strptime(input_date, "%Y-%m-%d").date()

        # When
        validated_epiweek = validate_epiweek(
            input_epiweek=epiweek, input_date=provided_date
        )

        # Then
        assert validated_epiweek == input_epiweek

    @pytest.mark.parametrize(
        "input_epiweek, input_date",
        (
            [1, "2022-11-01"],
            [2, "2022-11-09"],
            [3, "2022-11-18"],
            [4, "2022-11-20"],
            [5, "2022-12-09"],
            [6, "2022-12-14"],
            [7, "2022-12-31"],
            [9, "2023-01-01"],
            [9, "2023-01-02"],
            [10, "2023-01-09"],
        ),
    )
    def test_raises_error_for_invalid_date(self, input_epiweek: int, input_date: str):
        """
        Given an invalid pairing of epiweek and date
        When `validate_epiweek()` is called
        Then a `ValueError` is raised
        """
        # Given
        epiweek = input_epiweek
        provided_date = datetime.datetime.strptime(input_date, "%Y-%m-%d").date()

        # When / Then
        with pytest.raises(ValueError):
            validate_epiweek(input_epiweek=epiweek, input_date=provided_date)
