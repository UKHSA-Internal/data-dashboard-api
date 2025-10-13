import pytest
from pydantic_core._pydantic_core import ValidationError

from validation.data_transfer_models.base import IncomingBaseDataModel


class TestIncomingBaseValidationForChildTheme:
    @pytest.mark.parametrize(
        "parent_theme, child_theme, topic, metric, metric_group",
        (
            (
                "infectious_disease",
                "respiratory",
                "COVID-19",
                "COVID-19_testing_PCRcountByDay",
                "testing",
            ),
            (
                "infectious_disease",
                "vaccine_preventable",
                "Measles",
                "measles_cases_casesByOnsetWeek",
                "cases",
            ),
            (
                "infectious_disease",
                "bloodstream_infection",
                "E-coli",
                "e-coli_cases_countsByOnsetLocation",
                "cases",
            ),
            (
                "infectious_disease",
                "gastrointestinal",
                "C-difficile",
                "c-difficile_cases_countsByOnsetLocation",
                "cases",
            ),
            (
                "extreme_event",
                "weather_alert",
                "Heat-alert",
                "heat-alert_headline_matrixNumber",
                "headline",
            ),
            (
                "infectious_disease",
                "contact",
                "mpox-clade-1b",
                "mpox-clade-1b_cases_countByWeek",
                "cases",
            ),
            (
                "infectious_disease",
                "contact",
                "mpox-clade-1b",
                "mpox-clade-1b_headline_countTotal",
                "headline",
            ),
        ),
    )
    def test_child_theme_deemed_valid_for_parent_theme(
        self,
        parent_theme: str,
        child_theme: str,
        topic: str,
        metric: str,
        metric_group: str,
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
        payload["metric"] = metric
        payload["metric_group"] = metric_group

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(incoming_base_validation, strict=True)

    @pytest.mark.parametrize(
        "parent_theme, child_theme, topic, metric, metric_group",
        (
            (
                "infectious_disease",
                "weather_alert",
                "COVID-19",
                "COVID-19_testing_PCRcountByDay",
                "testing",
            ),
            (
                "extreme_event",
                "respiratory",
                "Measles",
                "measles_cases_casesByOnsetWeek",
                "cases",
            ),
            (
                "extreme_event",
                "vaccine_preventable",
                "Heat-alert",
                "heat-alert_headline_matrixNumber",
                "headline",
            ),
        ),
    )
    def test_raises_error_when_child_theme_invalid_choice_for_parent_theme(
        self,
        parent_theme: str,
        child_theme: str,
        topic: str,
        metric: str,
        metric_group: str,
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
        payload["metric"] = metric
        payload["metric_group"] = metric_group

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
