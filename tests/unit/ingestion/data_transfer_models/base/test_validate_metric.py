import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.utils.enums import DataSourceFileType


class TestIncomingBaseValidationForMetric:
    @pytest.mark.parametrize(
        "metric, metric_group",
        (
            ("COVID-19_deaths_ONSByDay", DataSourceFileType.deaths.value),
            ("influenza_headline_positivityLatest", DataSourceFileType.headline.value),
            ("RSV_healthcare_admissionRateByWeek", DataSourceFileType.healthcare.value),
            ("hMPV_testing_positivityByWeek", DataSourceFileType.testing.value),
            (
                "parainfluenza_headline_positivityLatest",
                DataSourceFileType.headline.value,
            ),
            ("adenovirus_testing_positivityByWeek", DataSourceFileType.testing.value),
            ("rhinovirus_headline_positivityLatest", DataSourceFileType.headline.value),
        ),
    )
    def test_metric_group_in_metric_name_is_deemed_valid(
        self,
        metric: str,
        metric_group: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing valid `metric` and `metric_group` values
            where the `metric_group` is in the `metric` name
        When the `IncomingBaseDataModel` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["metric_group"] = metric_group

        # / When
        incoming_base_validation = IncomingBaseDataModel(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "metric, metric_group",
        (
            ("COVID-19_deaths_ONSByDay", DataSourceFileType.cases.value),
            ("influenza_headline_positivityLatest", DataSourceFileType.testing.value),
            ("RSV_healthcare_admissionRateByWeek", DataSourceFileType.deaths.value),
            ("hMPV_testing_positivityByWeek", DataSourceFileType.headline.value),
            ("parainfluenza_headline_positivityLatest", DataSourceFileType.cases.value),
            (
                "adenovirus_testing_positivityByWeek",
                DataSourceFileType.healthcare.value,
            ),
            (
                "rhinovirus_headline_positivityLatest",
                DataSourceFileType.vaccinations.value,
            ),
        ),
    )
    def test_when_metric_group_not_in_metric_name_error_is_thrown(
        self,
        metric: str,
        metric_group: str,
        valid_payload_for_base_model: dict[str, str],
    ):
        """
        Given a payload containing a `metric` name
            which does not include the given `metric_group`
        When the `IncomingBaseDataModel` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric"] = metric
        payload["metric_group"] = metric_group

        # When
        with pytest.raises(ValidationError):
            IncomingBaseDataModel(**payload)
