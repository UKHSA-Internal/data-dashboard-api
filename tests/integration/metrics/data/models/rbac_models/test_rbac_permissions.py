import pytest
from metrics.data.models.rbac_models import (
    RBACPermission,
    AdminFormThemeError,
    AdminFormDuplicatePermissionError,
    AdminFormSubthemeAssocThemeError,
    AdminFormTopicAssocSubthemeError,
    AdminFormSubthemeAssocTopicError,
)

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


class TestRBACPermission:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.non_communicable = Theme.objects.create(name="non-communicable")
        self.respiratory = SubTheme.objects.create(
            name="respiratory", theme=self.non_communicable
        )
        self.asthma = Topic.objects.create(name="asthma", sub_theme=self.respiratory)
        self.asthma_syndromic = Metric.objects.create(
            name="asthma_syndromic_emergencyDepartment_countsByDay"
        )
        self.nation = GeographyType.objects.create(name="Nation")
        self.england = Geography.objects.create(name="England")
        self.all = Age.objects.create(name="all")
        self.default = Stratum.objects.create(name="default")

    @pytest.mark.django_db
    def test_create_api_permission(self):
        """
        Given valid RBAC permission attributes
        When a new permission is created
        Then it is successfully saved to the database
        And its string representation is correct
        """
        # Given / When
        permission = RBACPermission.objects.create(
            name="non-communicable_permission",
            theme=self.non_communicable,
            sub_theme=self.respiratory,
            topic=self.asthma,
            metric=self.asthma_syndromic,
            geography_type=self.nation,
            geography=self.england,
            age=self.all,
            stratum=self.default,
        )

        # Then
        assert RBACPermission.objects.count() == 1
        assert str(permission) == (
            "name=non-communicable_permission, "
            "theme=non-communicable, "
            "sub_theme=respiratory, "
            "topic=asthma, "
            "metric=asthma_syndromic_emergencyDepartment_countsByDay, "
            "geography_type=Nation, "
            "geography=England, "
            "age=all, "
            "stratum=default"
        )

    @pytest.mark.django_db
    def test_theme(self):
        """
        Given an RBACPermission without a theme
        When it is validated
        Then an AdminFormThemeError is raised
        """
        # Given / When / Then
        with pytest.raises(AdminFormThemeError):
            RBACPermission(name="invalid_permission").clean()

    @pytest.mark.django_db
    def test_subtheme(self):
        """
        Given an RBACPermission without a theme or subtheme
        When it is validated
        Then an AdminFormSubthemeAssocThemeError is raised
        """
        # Given / When / Then
        with pytest.raises(AdminFormSubthemeAssocThemeError):
            RBACPermission(
                name="invalid_permission", theme=self.non_communicable
            ).clean()

    @pytest.mark.django_db
    def test_subtheme(self):
        """
        Given an RBACPermission with a sub_theme that does not join to a parent theme
        When it is validated
        Then an AdminFormSubthemeAssocThemeError is raised
        """
        # Given
        extreme_event = Theme.objects.create(name="extreme_event")
        weather_alert = SubTheme.objects.create(
            name="weather_alert", theme=extreme_event
        )

        # When / Then
        with pytest.raises(AdminFormSubthemeAssocThemeError):
            RBACPermission(
                name="invalid_permission",
                theme=self.non_communicable,
                sub_theme=weather_alert,
            ).clean()

    @pytest.mark.django_db
    def test_subtheme_must_belong_to_theme(self):
        """
        Given a subtheme that belongs to a different theme
        When an RBACPermission is created with mismatched theme and subtheme
        Then an AdminFormSubthemeAssocThemeError is raised
        """
        # Given
        other_theme = Theme.objects.create(name="infectious_disease")
        invalid_sub_theme = SubTheme.objects.create(
            name="weather_alert", theme=other_theme
        )

        # When / Then
        with pytest.raises(AdminFormSubthemeAssocThemeError):
            RBACPermission(
                name="invalid_permission",
                theme=self.non_communicable,
                sub_theme=invalid_sub_theme,
            ).clean()

    @pytest.mark.django_db
    def test_topic_subtheme_must_have_associated_theme(self):
        """
        Given a topic whose subtheme belongs to a different theme
        When an RBACPermission is created with mismatched topic and subtheme
        Then an AdminFormTopicAssocSubthemeError is raised
        """
        # Given
        other_theme = Theme.objects.create(name="infectious_disease")
        other_sub_theme = SubTheme.objects.create(name="respiratory", theme=other_theme)
        topic_with_different_theme = Topic.objects.create(
            name="E-coli", sub_theme=other_sub_theme
        )

        # When / Then
        with pytest.raises(AdminFormTopicAssocSubthemeError):
            RBACPermission(
                name="invalid_topic_permission",
                theme=self.non_communicable,
                sub_theme=self.respiratory,
                topic=topic_with_different_theme,
            ).clean()

    @pytest.mark.django_db
    def test_subtheme_must_have_associated_topic(self):
        """
        Given a subtheme that has no associated topic
        When an RBACPermission is created referencing this subtheme
        Then an AdminFormSubthemeAssocTopicError is raised
        """
        # Given
        sub_theme_without_topic = SubTheme.objects.create(
            name="mpox-clade-1b", theme=self.non_communicable
        )

        # When / Then
        with pytest.raises(AdminFormSubthemeAssocTopicError):
            RBACPermission(
                name="invalid_subtheme_permission",
                theme=self.non_communicable,
                sub_theme=sub_theme_without_topic,
                topic=self.asthma,
            ).clean()

    @pytest.mark.django_db
    def test_duplicate_permission_not_allowed(self):
        """
        Given an existing RBACPermission with a specific combination of attributes
        When another permission with the same attributes is created
        Then an AdminFormDuplicatePermissionError is raised
        """
        # Given
        RBACPermission.objects.create(
            name="unique_permission",
            theme=self.non_communicable,
            sub_theme=self.respiratory,
            topic=self.asthma,
            metric=self.asthma_syndromic,
            geography_type=self.nation,
            geography=self.england,
            age=self.all,
            stratum=self.default,
        )

        # When / Then
        with pytest.raises(AdminFormDuplicatePermissionError):
            RBACPermission(
                name="duplicate_permission",
                theme=self.non_communicable,
                sub_theme=self.respiratory,
                topic=self.asthma,
                metric=self.asthma_syndromic,
                geography_type=self.nation,
                geography=self.england,
                age=self.all,
                stratum=self.default,
            ).clean()
