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


class TestNonPublicDataTrendsAPI:
    @property
    def path(self) -> str:
        return "/api/trends/v3"

    @classmethod
    def get_valid_payload(cls, core_main_headline, core_percentage_headline) -> dict:
        return {
            "topic": core_main_headline.metric.topic.name,
            "metric": core_main_headline.metric.name,
            "percentage_metric": core_percentage_headline.metric.name,
            "geography": core_main_headline.geography.name,
            "geography_type": core_main_headline.geography.geography_type.name,
            "age": core_main_headline.age.name,
            "sex": core_main_headline.sex,
            "stratum": core_main_headline.stratum.name,
        }

    @pytest.mark.django_db
    @mock.patch.object(auth, "AUTH_ENABLED")
    def test_trends_endpoint_returns_non_public_data_with_valid_permissions(
        self, mocked_auth_enabled: mock.MagicMock
    ):
        """
        Given auth is enabled
        And public & non-public `CoreHeadline` records
        And the required RBAC permission has been granted
        When the `trends/v3` endpoint is hit
        Then the response returns the non-public records
        When the permission is removed
        And the `trends/v3` endpoint is hit again
        Then the response returns the public records instead
        """
        # Given
        mocked_auth_enabled.return_value = True
        client = APIClient()
        group_id = uuid.uuid4()

        main_metric_public_record = CoreHeadlineFactory.create_record(
            metric="COVID-19_headline_cases_7DayChange",
            metric_value=1,
            period_end="2025-01-01",
            is_public=True,
        )
        percentage_metric_public_record = CoreHeadlineFactory.create_record(
            metric="COVID-19_headline_cases_7DayPercentChange",
            metric_value=2,
            period_end="2025-01-01",
            is_public=True,
        )

        main_metric_non_public_record = CoreHeadlineFactory.create_record(
            metric="COVID-19_headline_cases_7DayChange",
            metric_value=3,
            period_end="2025-01-02",
            is_public=False,
        )
        percentage_metric_non_public_record = CoreHeadlineFactory.create_record(
            metric="COVID-19_headline_cases_7DayPercentChange",
            metric_value=4,
            period_end="2025-01-02",
            is_public=False,
        )

        permission = RBACPermissionFactory.create(
            name="valid permission",
            theme=main_metric_public_record.metric.topic.sub_theme.theme,
        )
        rbac_group = RBACGroupPermissionFactory.create_record(
            name="Test group",
            group_id=group_id,
            permissions=[permission],
        )
        payload = self.get_valid_payload(
            core_main_headline=main_metric_public_record,
            core_percentage_headline=percentage_metric_public_record,
        )

        # Whens
        response: Response = client.get(
            path=self.path,
            data=payload,
            headers={RBAC_AUTH_X_HEADER: group_id},
        )

        # Then
        results = response.data
        assert results["metric_name"] == main_metric_public_record.metric.name
        assert (
            results["percentage_metric_name"]
            == percentage_metric_public_record.metric.name
        )

        # The non public records are returned since the group has the requisite permissions
        assert (
            results["metric_value"]
            == main_metric_non_public_record.metric_value
            != main_metric_public_record.metric_value
        )
        assert (
            results["metric_period_end"].strftime(EXPECTED_DATE_FORMAT)
            == main_metric_non_public_record.period_end
            != main_metric_public_record.period_end
        )

        assert (
            results["percentage_metric_value"]
            == percentage_metric_non_public_record.metric_value
            != percentage_metric_public_record.metric_value
        )
        assert (
            results["percentage_metric_period_end"].strftime(EXPECTED_DATE_FORMAT)
            == percentage_metric_non_public_record.period_end
            != percentage_metric_public_record.period_end
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
        # This time around the public records will be returned
        results = response.data
        assert (
            results["metric_value"]
            == main_metric_public_record.metric_value
            != main_metric_non_public_record.metric_value
        )
        assert (
            results["metric_period_end"].strftime(EXPECTED_DATE_FORMAT)
            == main_metric_public_record.period_end
            != main_metric_non_public_record.period_end
        )

        assert (
            results["percentage_metric_value"]
            == percentage_metric_public_record.metric_value
            != percentage_metric_non_public_record.metric_value
        )
        assert (
            results["percentage_metric_period_end"].strftime(EXPECTED_DATE_FORMAT)
            == percentage_metric_public_record.period_end
            != percentage_metric_non_public_record.period_end
        )
