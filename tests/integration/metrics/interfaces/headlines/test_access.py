from unittest import mock

import pytest
from django.test import RequestFactory
from rest_framework.request import Request

from metrics.domain.headlines.state import Headline
from metrics.domain.models.headline import HeadlineParameters
from metrics.interfaces.headlines.access import HeadlinesInterface
from tests.factories.metrics.headline import CoreHeadlineFactory
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory

MODULE_PATH = "metrics.interfaces.headlines.access"


class TestHeadlinesInterface:
    @pytest.mark.django_db
    @mock.patch(f"{MODULE_PATH}.is_auth_enabled")
    def test_get_latest_metric_value_returns_non_public_record_for_matching_permission(
        self, mocked_is_auth_enabled: mock.MagicMock
    ):
        """
        Given public and non-public `CoreHeadline` records
        And an `RBACPermission` which gives access to the non-public portion of the data
        And `AUTH_ENABLED` is set to True
        When `get_latest_metric_value()` is called from the `HeadlinesInterface`
        Then the non-public record is returned
        """
        # Given
        mocked_is_auth_enabled.return_value = True
        public_record = CoreHeadlineFactory.create_record(
            period_end="2025-01-01", metric_value=1, is_public=True
        )
        non_public_record = CoreHeadlineFactory.create_record(
            period_end="2025-01-02", metric_value=2, is_public=False
        )
        rbac_permission = RBACPermissionFactory.create_record(
            theme_name=public_record.metric.topic.sub_theme.theme.name,
            sub_theme_name=public_record.metric.topic.sub_theme.name,
            topic_name=public_record.metric.topic.name,
            metric_name=public_record.metric.name,
            geography_name=public_record.geography.name,
            geography_type_name=public_record.geography.geography_type.name,
        )

        request_factory = RequestFactory()
        fake_request = Request(request=request_factory.get("/"))
        fake_request.rbac_permissions = [rbac_permission]

        headline_parameters = HeadlineParameters(
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            stratum=public_record.stratum.name,
            age=public_record.age.name,
            sex=public_record.sex,
            geography=public_record.geography.name,
            geography_type=public_record.geography.geography_type.name,
            request=fake_request,
        )
        headlines_interface = HeadlinesInterface(
            headline_parameters=headline_parameters
        )

        # When
        headline: Headline = headlines_interface.get_latest_metric_value()

        # Then
        assert (
            headline.metric_value
            == non_public_record.metric_value
            != public_record.metric_value
        )

    @pytest.mark.django_db
    @mock.patch(f"{MODULE_PATH}.is_auth_enabled")
    def test_get_latest_metric_value_excludes_non_public_record_for_no_matching_permission(
        self, mocked_is_auth_enabled: mock.MagicMock
    ):
        """
        Given public and non-public `CoreHeadline` records
        And no `RBACPermission` which allows access to the non-public portion of this dataset
        And `AUTH_ENABLED` is set to True
        When `get_latest_metric_value()` is called from the `HeadlinesInterface`
        Then the non-public record is excluded
        """
        # Given
        mocked_is_auth_enabled.return_value = True
        public_record = CoreHeadlineFactory.create_record(
            period_end="2025-01-01", metric_value=1, is_public=True
        )
        non_public_record = CoreHeadlineFactory.create_record(
            period_end="2025-01-02", metric_value=2, is_public=False
        )

        request_factory = RequestFactory()
        fake_request = Request(request=request_factory.get("/"))
        fake_request.rbac_permissions = []

        headline_parameters = HeadlineParameters(
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            stratum=public_record.stratum.name,
            age=public_record.age.name,
            sex=public_record.sex,
            geography=public_record.geography.name,
            geography_type=public_record.geography.geography_type.name,
            request=fake_request,
        )
        headlines_interface = HeadlinesInterface(
            headline_parameters=headline_parameters
        )

        # When
        headline: Headline = headlines_interface.get_latest_metric_value()

        # Then
        assert (
            headline.metric_value
            == public_record.metric_value
            != non_public_record.metric_value
        )
