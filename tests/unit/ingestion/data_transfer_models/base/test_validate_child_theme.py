import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.utils.enums import DataSourceFileType, Topic


class TestIncomingBaseValidationForChildTheme:
    @pytest.mark.parametrize(
        "parent_theme, child_theme, topic",
        (
            ("infectious_disease", "respiratory", "COVID-19"),
            ("infectious_disease", "vaccine_preventable", "Measles"),
            ("extreme_event", "weather_alert", "Heat-alert"),
        ),
    )
    def test_child_theme_deemed_valid_infectious_disease(
        self,
        parent_theme: str,
        child_theme: str,
        topic: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing a valid `child_theme`, `parent_theme` and `topic`
            combination
        When the `IncomingBaseDataModel` model is initialized
        Then the model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme
        payload["topic"] = topic

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(incoming_base_validation, strict=True)

    @pytest.mark.parametrize(
        "parent_theme, child_theme, topic",
        (
            ("infectious_disease", "weather_alert", "COVID-19"),
            ("extreme_event", "respiratory", "Measles"),
            ("extreme_event", "vaccine_preventable", "Heat-alert"),
        ),
    )
    def test_raises_error_when_child_theme_invalid_choice_for_parent_theme(
        self,
        parent_theme: str,
        child_theme: str,
        topic: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing an invalid `child_theme` and `parent_theme`
            combination
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme
        payload["topic"] = topic

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
