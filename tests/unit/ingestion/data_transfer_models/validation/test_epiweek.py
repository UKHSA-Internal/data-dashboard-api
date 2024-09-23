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
