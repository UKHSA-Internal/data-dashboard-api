import pytest
from metrics.data.models.rbac_models import RBACGroupPermission, RBACPermission
from metrics.data.models.core_models import (
    Theme,
    SubTheme,
    Topic,
    Metric,
    GeographyType,
    Geography,
    Age,
    Stratum,
)


class TestRBACGroupPermission:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.theme = Theme.objects.create(name="non-communicable")
        self.sub_theme = SubTheme.objects.create(name="respiratory", theme=self.theme)
        self.topic = Topic.objects.create(name="asthma", sub_theme=self.sub_theme)
        self.metric1 = Metric.objects.create(
            name="COVID-19_vaccinations_autumn22_dosesByDay"
        )
        self.metric2 = Metric.objects.create(name="COVID-19_deaths_ONSByWeek")

        self.geography_type = GeographyType.objects.create(name="Nation")
        self.geography = Geography.objects.create(name="England")
        self.age = Age.objects.create(name="all")
        self.stratum = Stratum.objects.create(name="default")

        self.permission_dose_by_day = RBACPermission.objects.create(
            name="asthma_permission_1",
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic,
            metric=self.metric1,
            geography_type=self.geography_type,
            geography=self.geography,
            age=self.age,
            stratum=self.stratum,
        )

        self.permission_ons_by_week = RBACPermission.objects.create(
            name="asthma_permission_2",
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic,
            metric=self.metric2,
            geography_type=self.geography_type,
            geography=self.geography,
            age=self.age,
            stratum=self.stratum,
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
        with pytest.raises(Exception):  # Adjust exception type based on DB backend
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

        # Then ensure both permissions are stored
        assert rbac_group.permissions.count() == 2
        assert self.permission_dose_by_day in rbac_group.permissions.all()
        assert self.permission_ons_by_week in rbac_group.permissions.all()
