import pytest
from django.db.utils import IntegrityError

from tests.factories.metrics.time_series import CoreTimeSeriesFactory
from metrics.data.models.rbac_models import RBACGroupPermission, RBACPermission
from metrics.data.models.core_models import (
    Theme,
    SubTheme,
    Topic,
)


class TestRBACGroupPermission:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.non_communicable = Theme.objects.create(name="non-communicable")
        self.respiratory = SubTheme.objects.create(
            name="respiratory", theme=self.non_communicable
        )
        self.asthma = Topic.objects.create(name="asthma", sub_theme=self.respiratory)
        self.covid_cases_dose_by_day = CoreTimeSeriesFactory.create_record(
            theme_name=self.non_communicable.name,
            sub_theme_name=self.respiratory.name,
            topic_name=self.asthma.name,
            metric_name="COVID-19_vaccinations_autumn22_dosesByDay",
            geography_type_name="Nation",
            geography_name="England",
            age_name="all",
            stratum_name="default",
        )

        self.covid_cases_ons_by_week = CoreTimeSeriesFactory.create_record(
            theme_name=self.non_communicable.name,
            sub_theme_name=self.respiratory.name,
            topic_name=self.asthma.name,
            metric_name="COVID-19_deaths_ONSByWeek",
        )

        self.permission_dose_by_day = RBACPermission.objects.create(
            name="asthma_permission_1",
            theme=self.non_communicable,
            sub_theme=self.respiratory,
            topic=self.asthma,
            metric=self.covid_cases_dose_by_day.metric,
        )

        self.permission_ons_by_week = RBACPermission.objects.create(
            name="asthma_permission_2",
            theme=self.non_communicable,
            sub_theme=self.respiratory,
            topic=self.asthma,
            metric=self.covid_cases_ons_by_week.metric,
        )

    @pytest.mark.django_db
    def test_create_rbac_group_permission(self):
        """
        Given a valid RBACPermission instance
        When an RBACGroupPermission is created
        Then it should be saved successfully with the correct name
        And should be retrievable from the database
        """
        # When
        group = RBACGroupPermission.objects.create(name="admin_group")
        group.permissions.add(self.permission_dose_by_day)

        # Then
        assert RBACGroupPermission.objects.count() == 1
        assert group.name == "admin_group"
        assert self.permission_dose_by_day in group.permissions.all()

    @pytest.mark.django_db
    def test_rbac_group_permission_must_have_unique_name(self):
        """
        Given an existing RBACGroupPermission
        When another group with the same name is attempted to be created
        Then a database IntegrityError should be raised
        """
        # Given
        RBACGroupPermission.objects.create(name="duplicate_group")

        # When / Then
        with pytest.raises(IntegrityError):  # Adjust exception type based on DB backend
            RBACGroupPermission.objects.create(name="duplicate_group")

    @pytest.mark.django_db
    def test_rbac_group_can_have_multiple_permissions(self):
        """
        Given an `RBACGroupPermission`
        When multiple unique `RBACPermission` instances are added
        Then the group successfully stores and retrieves all permissions
        """
        # Given
        rbac_group = RBACGroupPermission.objects.create(name="respiratory_admins")
        rbac_group.permissions.add(
            self.permission_dose_by_day, self.permission_ons_by_week
        )

        # When / Then
        assert rbac_group.permissions.count() == 2
        assert self.permission_dose_by_day in rbac_group.permissions.all()
        assert self.permission_ons_by_week in rbac_group.permissions.all()
