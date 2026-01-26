import uuid
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.decorators.auth import RBAC_AUTH_X_HEADER
from metrics.api.settings import auth
from tests.factories.metrics.headline import CoreHeadlineFactory
from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACGroupPermissionFactory,
)
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory

EXPECTED_DATE_FORMAT = "%Y-%m-%d"


class TestNonPublicDataHeadlinesAPI:
    @property
    def path(self) -> str:
        return "/api/headlines/v3"

    @classmethod
    def get_valid_payload(cls, core_headline) -> dict:
        return {
            "topic": core_headline.metric.topic.name,
            "metric": core_headline.metric.name,
            "geography": core_headline.geography.name,
            "geography_type": core_headline.geography.geography_type.name,
            "age": core_headline.age.name,
            "sex": core_headline.sex,
            "stratum": core_headline.stratum.name,
        }

    @pytest.mark.django_db
    @mock.patch.object(auth, "AUTH_ENABLED")
    def test_headlines_endpoint_returns_non_public_data_with_valid_permissions(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given auth is enabled
        And public & non-public `CoreHeadline` records
        And the required RBAC permission has been granted
        When the `headlines/v3` endpoint is hit
        Then the response returns the non-public record
        When the permission is removed
        And the `headlines/v3` endpoint is hit again
        Then the response returns the public record instead
        """
        # Given
        mocked_auth_enabled.return_value = True
        client = APIClient()
        group_id = uuid.uuid4()

        public_record = CoreHeadlineFactory.create_record(
            metric_value=1, period_end="2025-01-01", is_public=True
        )
        non_public_record = CoreHeadlineFactory.create_record(
            metric_value=2, period_end="2025-01-02", is_public=False
        )

        permission = RBACPermissionFactory.create(
            name="valid permission",
            theme=public_record.metric.topic.sub_theme.theme,
        )
        rbac_group = RBACGroupPermissionFactory.create_record(
            name="Test group",
            group_id=group_id,
            permissions=[permission],
        )
        payload = self.get_valid_payload(core_headline=public_record)

        # When
        response: Response = client.get(
            path=self.path,
            data=payload,
            headers={RBAC_AUTH_X_HEADER: group_id},
        )

        # Then
        results = response.data
        assert (
            results["value"]
            == non_public_record.metric_value
            != public_record.metric_value
        )
        assert (
            results["period_end"].strftime(EXPECTED_DATE_FORMAT)
            == non_public_record.period_end
            != public_record.period_end
        )

        # Remove the permission from the group
        rbac_group.permissions.clear()
        rbac_group.save()

        # When
        response: Response = client.get(
            path=self.path,
            data=payload,
            headers={RBAC_AUTH_X_HEADER: group_id},
        )

        # Then
        # This time around the public record will be returned
        result = response.data
        assert (
            result["value"]
            == public_record.metric_value
            != non_public_record.metric_value
        )
        assert (
            result["period_end"].strftime(EXPECTED_DATE_FORMAT)
            == public_record.period_end
            != non_public_record.period_end
        )
