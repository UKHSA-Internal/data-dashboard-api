import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.metrics_interface.interface import DataSourceFileType


class TestIncomingBaseValidationForMetricProperty:
    @pytest.mark.parametrize(
        "metric, topic, metric_group, parent_theme, child_theme",
        (
            (
                "COVID-19_deaths_ONSByDay",
                "COVID-19",
                DataSourceFileType.deaths.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "influenza_headline_positivityLatest",
                "Influenza",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "RSV_healthcare_admissionRateByWeek",
                "RSV",
                DataSourceFileType.healthcare.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "hMPV_testing_positivityByWeek",
                "hMPV",
                DataSourceFileType.testing.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "parainfluenza_headline_postitivityLatest",
                "Parainfluenza",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "adenovirus_testing_positivityByWeek",
                "Adenovirus",
                DataSourceFileType.testing.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "rhinovirus_headline_positivityLatest",
                "Rhinovirus",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "heat-alert_headline_matrixNumber",
                "Heat-alert",
                DataSourceFileType.headline.value,
                "extreme_event",
                "weather_alert",
            ),
            (
                "cold-alert_headline_matrixNumber",
                "Cold-alert",
                DataSourceFileType.headline.value,
                "extreme_event",
                "weather_alert",
            ),
        ),
    )
    def test_valid_payload_is_deemed_valid(
        self,
        metric: str,
        topic: str,
        metric_group: str,
        parent_theme: str,
        child_theme: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a valid payload including matching `topic` and `metric_group`
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["topic"] = topic
        payload["metric_group"] = metric_group
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme

        # When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "metric, topic, metric_group, parent_theme, child_theme",
        (
            (
                "COVID-19_deaths_ONSByDay",
                "Influenza",
                DataSourceFileType.deaths.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "influenza_headline_positivityLatest",
                "COVID-19",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "RSV_healthcare_admissionRateByWeek",
                "Influenza",
                DataSourceFileType.healthcare.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "heat-alert_headline_matrixNumber",
                "Cold-alert",
                DataSourceFileType.headline.value,
                "extreme_event",
                "weather_alert",
            ),
        ),
    )
    def test_when_topic_not_in_metric_an_error_is_thrown(
        self,
        metric: str,
        topic: str,
        metric_group: str,
        parent_theme: str,
        child_theme: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a `metric` that does not contain the given `topic` name
        When the `IncomingBaseDataModel` model is initialized
        Then and `ValueError` is thrown
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["topic"] = topic
        payload["metric_group"] = metric_group
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "metric, topic, metric_group, parent_theme, child_theme",
        (
            (
                "COVID-19_deaths_ONSByDay",
                "COVID-19",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "influenza_headline_positivityLatest",
                "Influenza",
                DataSourceFileType.cases.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "RSV_healthcare_admissionRateByWeek",
                "RSV",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "heat-alert_headline_matrixNumber",
                "Heat-alert",
                DataSourceFileType.deaths.value,
                "extreme_event",
                "weather_alert",
            ),
        ),
    )
    def test_when_metric_group_not_in_metric_an_error_is_thrown(
        self,
        metric: str,
        topic: str,
        metric_group: str,
        parent_theme: str,
        child_theme: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a `metric` that does not contain the given `metric_group`
        When the `IncomingBaseDataModel` model is initialized
        Then and `ValueError` is thrown
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["topic"] = topic
        payload["metric_group"] = metric_group
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "metric, topic, metric_group, parent_theme, child_theme",
        (
            (
                "COVID-19_deaths_ONS-ByDay",
                "COVID-19",
                DataSourceFileType.deaths.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "influenza_headline_positivity&Latest",
                "Influenza",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "RSV_healthcare_admissionRateByWeek$!_invalid",
                "RSV",
                DataSourceFileType.healthcare.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "heat-alert_headline_matrix-Number",
                "Heat-alert",
                DataSourceFileType.headline.value,
                "extreme_event",
                "weather_alert",
            ),
        ),
    )
    def test_when_metric_includes_special_characters_an_error_is_thrown(
        self,
        metric: str,
        topic: str,
        metric_group: str,
        parent_theme: str,
        child_theme: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given an invalid `metric` where the `metric_detail` is not alphanumeric
            and includes special characters apart from `_`.
        When the `IncomingBaseDataModel` model is initialized
        Then and `ValueError` is thrown
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["topic"] = topic
        payload["metric_group"] = metric_group
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)

    @pytest.mark.parametrize(
        "metric, topic, metric_group, parent_theme, child_theme",
        (
            (
                "COVID-19_deaths",
                "COVID-19",
                DataSourceFileType.deaths.value,
                "infectious_disease",
                "respiratory",
            ),
            (
                "influenza_headline",
                "Influenza",
                DataSourceFileType.headline.value,
                "infectious_disease",
                "respiratory",
            ),
        ),
    )
    def test_when_incorrect_metric_structure_error_is_thrown(
        self,
        metric: str,
        topic: str,
        metric_group: str,
        parent_theme: str,
        child_theme: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given an invalid metric that does not include 3 or more sections
        When the `IncomingBaseDataModel` model is initialized
        Then and `ValueError` is thrown
        """
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["topic"] = topic
        payload["metric_group"] = metric_group
        payload["parent_theme"] = parent_theme
        payload["child_theme"] = child_theme

        # When / Then
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
