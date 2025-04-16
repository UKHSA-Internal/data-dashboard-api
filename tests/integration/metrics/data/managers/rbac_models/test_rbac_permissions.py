import pytest

from metrics.data.models.rbac_models import (
    RBACPermission,
    DuplicatePermissionError,
)
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory


class TestRBACPermissionFactory:

    permissions = {
        "theme_name": "infectious_disease",
        "sub_theme_name": "respiratory",
        "topic_name": "COVID-19",
        "metric_name": "COVID-19_headline_positivity_latest",
        "geography_type_name": "Nation",
        "geography_name": "England",
    }

    @pytest.mark.django_db
    def test_create_record_creates_valid_permission(self):
        """
        Given valid input parameters,
        When `create_record` is called,
        Then an `RBACPermission` instance is created with the correct associations.
        """
        # Given
        permission = RBACPermissionFactory.create_record(**self.permissions)

        # When
        assert RBACPermission.objects.filter(id=permission.id).exists()

        # Then
        assert permission.theme.name == "infectious_disease"
        assert permission.sub_theme.name == "respiratory"
        assert permission.topic.name == "COVID-19"
        assert permission.metric.name == "COVID-19_headline_positivity_latest"
        assert permission.geography.name == "England"
        assert permission.geography_type.name == "Nation"

    @pytest.mark.django_db
    def test_get_existing_permissions_returns_no_queryset(self):
        """
        Given multiple `RBACPermission` records with overlapping fields
        And a unique `RBACPermission` record
        When `get_existing_permissions()` is called
        Then only the records with matching fields (excluding the given instance) are returned
        """
        # Given
        permission = RBACPermissionFactory.create_record()

        RBACPermissionFactory.create_record(
            name="permission_2",
            theme_name="extreme_event",
            sub_theme_name="weather_alert",
        )
        # When
        retrieved_permissions = RBACPermission.objects.get_existing_permissions(
            instance=permission
        )

        # Then
        assert retrieved_permissions.count() == 0

    @pytest.mark.django_db
    def test_create_duplicate_permission_raises_error(self):
        """
        Given an existing `RBACPermission` record with specific fields,
        When another permission with the same fields is created,
        Then an `AdminFormDuplicatePermissionError` should be raised.
        """
        # Given
        RBACPermissionFactory.create_record(
            name="all_infectious_respiratory_data",
            theme_name="infectious_disease",
            sub_theme_name="respiratory",
        )

        # When / Then
        with pytest.raises(DuplicatePermissionError):
            RBACPermissionFactory.create_record(
                name="all_infectious_respiratory_data_duplicate",
                theme_name="infectious_disease",
                sub_theme_name="respiratory",
            )
