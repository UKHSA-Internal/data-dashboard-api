import uuid
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.decorators.auth import RBAC_AUTH_X_HEADER
from metrics.api.settings import auth
from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACPermissionGroupFactory,
)
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestNonPublicDataDownloadsAPI:
    @property
    def path(self) -> str:
        return "/api/downloads/v2"

    @classmethod
    def get_valid_payload(cls, core_time_series) -> dict:
        return {
            "file_format": "json",
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
                }
            ],
        }

    @pytest.mark.django_db
    @mock.patch.object(auth, "AUTH_ENABLED")
    def test_downloads_endpoint_returns_non_public_data_with_valid_permissions(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given auth is enabled
        And public & non-public `CoreTimeSeries` records
        And the required RBAC permission has been granted
        When the `downloads/v2` endpoint is hit
        Then the returned response includes the non-public record
        """
        # Given
        mocked_auth_enabled.return_value = True
        client = APIClient()
        group_id = uuid.uuid4()

        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1, date="2025-01-01", is_public=True
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            metric_value=2, date="2025-01-02", is_public=False
        )

        permission = RBACPermissionFactory.create(
            name="valid permission",
            theme=public_record.metric.topic.sub_theme.theme,
        )
        RBACPermissionGroupFactory.create_record(
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
        assert len(results) == 2
        assert results[0]["date"] == non_public_record.date
        assert (
            results[0]["metric_value"] == f"{non_public_record.metric_value:.4f}"
        )

        assert results[1]["date"] == public_record.date
        assert results[1]["metric_value"] == f"{public_record.metric_value:.4f}"

    @pytest.mark.django_db
    @mock.patch.object(auth, "AUTH_ENABLED")
    def test_downloads_endpoint_excludes_non_public_data_without_valid_permissions(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given auth is enabled
        And public & non-public `CoreTimeSeries` records
        And the required RBAC permission has not been granted
        When the `downloads/v2` endpoint is hit
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

        RBACPermissionGroupFactory.create_record(
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
        assert len(results) == 1
        assert results[0]["date"] == public_record.date
        assert results[0]["metric_value"] == f"{public_record.metric_value:.4f}"
