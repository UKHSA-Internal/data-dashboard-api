import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel


class TestIncomingBaseValidationForTopic:

    @pytest.mark.parametrize(
        "topic, metric",
        (
            ("COVID-19", "COVID-19_testing_PCRcountByDay"),
            ("Influenza", "influenza_testing_positivityByWeek"),
            ("RSV", "RSV_testing_positivityByWeek"),
            ("hMPV", "hMPV_testing_positivityByWeek"),
            ("Parainfluenza", "parainfluenza_testing_positivityByWeek"),
            ("Adenovirus", "adenovirus_testing_positivityByWeek"),
            ("Rhinovirus", "rhinovirus_testing_positivityByWeek"),
        ),
    )
    def test_valid_topic_values_are_deemed_valid(
        self, topic: str, metric: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing valid `topic` and `metric` values
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["topic"] = topic
        payload["metric"] = metric

        # / When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "topic, metric",
        (
            ("covid_19", "COVID-19_testing_PCRcountByDay"),
            ("covid-19", "COVID-19_testing_PCRcountByDay"),
            ("covid-10", "COVID-19_testing_PCRcountByDay"),
            ("covid-20", "COVID-19_testing_PCRcountByDay"),
            ("coronavirus", "COVID-19_testing_PCRcountByDay"),
            ("Coronavirus", "COVID-19_testing_PCRcountByDay"),
            ("CORONAVIRUS", "COVID-19_testing_PCRcountByDay"),
            ("influenza", "influenza_testing_positivityByWeek"),
            ("INFLUENZA", "influenza_testing_positivityByWeek"),
            ("rsv", "RSV_testing_positivityByWeek"),
            ("HMPV", "hMPV_testing_positivityByWeek"),
            ("hmpv", "hMPV_testing_positivityByWeek"),
            ("parainfluenza", "parainfluenza_testing_positivityByWeek"),
            ("PARAINFLUENZA", "parainfluenza_testing_positivityByWeek"),
            ("ADENOVIRUS", "adenovirus_testing_positivityByWeek"),
            ("adenovirus", "adenovirus_testing_positivityByWeek"),
            ("rhinovirus", "rhinovirus_testing_positivityByWeek"),
            ("RHINOVIRUS", "rhinovirus_testing_positivityByWeek"),
        ),
    )
    def test_invalid_topic_values_throw_error(
        self, topic: str, metric: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing an invalid `topic`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["topic"] = topic
        payload["metric"] = metric

        # When
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
