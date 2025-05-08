
import uuid
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.decorators.auth import RBAC_AUTH_X_HEADER
from metrics.api.settings import auth
from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACGroupPermissionFactory,
)
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestNonPublicDataChartsAPI:
    @property
    def path(self) -> str:
        return "/api/charts/v3"

    @classmethod
    def get_valid_payload(cls, core_time_series) -> dict:
        return {
            "file_format": "svg",
            "plots": [
                {
                    "metric": core_time_series.metric.name,
                    "topic": core_time_series.metric.topic.name,
                    "stratum": core_time_series.stratum.name,
                    "age": core_time_series.age.name,
                    "sex": core_time_series.sex,
                    "geography": core_time_series.geography.name,
                    "geography_type": core_time_series.geography.geography_type.name,
                    "date_from": "2000-01-01",
                    "date_to": "2025-12-31",
                    "chart_type": "bar",
                }
            ],
        }

    @pytest.mark.django_db
    @mock.patch.object(auth, "AUTH_ENABLED")
    def test_charts_endpoint_returns_non_public_data_with_valid_permissions(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given auth is enabled
        And public & non-public `CoreTimeSeries` records
        And the required RBAC permission has been granted
        When the `charts/v3` endpoint is hit
        Then the returned response includes the non-public record
        """
        # Given
        mocked_auth_enabled.return_value = True
        client = APIClient()
        group_id = uuid.uuid4()

        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1, date="2025-01-01", is_public=True
        )
        CoreTimeSeriesFactory.create_record(
            metric_value=2, date="2025-01-02", is_public=False
        )

        permission = RBACPermissionFactory.create(
            name="valid permission",
            theme=public_record.metric.topic.sub_theme.theme,
        )
        RBACGroupPermissionFactory.create_record(
            name="Test group",
            group_id=group_id,
            permissions=[permission],
        )
        payload = self.get_valid_payload(core_time_series=public_record)

        # When
        response: Response = client.post(
            path=self.path,
            data=payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: group_id},
        )

        # Then
        results = response.data
        # Check that both records are referenced in the alt text
        alt_text: str = results["alt_text"]
        assert "1.0 on 01 January 2025" in alt_text
        assert "2.0 on 02 January 2025" in alt_text

        # Check that both records are shown on the chart itself
        figure = results["figure"]
        x_axis_data: list[str] = figure["data"][0]["x"]
        assert "2025-01-01" in x_axis_data
        assert "2025-01-02" in x_axis_data

        y_axis_data: list[float] = figure["data"][0]["y"]
        assert 1.0 in y_axis_data
        assert 2.0 in y_axis_data

    @pytest.mark.django_db
    @mock.patch.object(auth, "AUTH_ENABLED")
    def test_charts_endpoint_excludes_non_public_data_without_valid_permissions(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given auth is enabled
        And public & non-public `CoreTimeSeries` records
        And the required RBAC permission has not been granted
        When the `charts/v3` endpoint is hit
        Then the returned response excludes the non-public record
        """
        # Given
        mocked_auth_enabled.return_value = True
        client = APIClient()
        group_id = uuid.uuid4()

        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1, date="2025-01-01", is_public=True
        )
        CoreTimeSeriesFactory.create_record(
            metric_value=2, date="2025-01-02", is_public=False
        )

        RBACGroupPermissionFactory.create_record(
            name="Test group",
            group_id=group_id,
            permissions=[],
        )
        payload = self.get_valid_payload(core_time_series=public_record)

        # When
        response: Response = client.post(
            path=self.path,
            data=payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: group_id},
        )

        # Then
        results = response.data
        # Check that only the public record is referenced in the alt text
        alt_text: str = results["alt_text"]
        assert "1.0 on 01 January 2025" in alt_text
        assert "2.0 on 02 January 2025" not in alt_text

        # Check that only the public record is shown on the chart itself
        figure = results["figure"]
        x_axis_data: list[str] = figure["data"][0]["x"]
        assert "2025-01-01" in x_axis_data
        assert "2025-01-02" not in x_axis_data

        y_axis_data: list[float] = figure["data"][0]["y"]
        assert 1.0 in y_axis_data
        assert 2.0 not in y_axis_data
