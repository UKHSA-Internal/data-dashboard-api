import pytest
from metrics.data.models.rbac_models import (
    RBACPermission,
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
        """
        Given a set of core model instances,
        When a test case is executed,
        Then the test cases should have access to these predefined instances.
        """
        self.theme = Theme.objects.create(name="non-communicable")
        self.sub_theme = SubTheme.objects.create(name="respiratory", theme=self.theme)
        self.topic = Topic.objects.create(name="asthma", sub_theme=self.sub_theme)
        self.metric = Metric.objects.create(
            name="asthma_syndromic_emergencyDepartment_countsByDay"
        )
        self.geography_type = GeographyType.objects.create(name="Nation")
        self.geography = Geography.objects.create(name="England")
        self.age = Age.objects.create(name="all")
        self.stratum = Stratum.objects.create(name="default")

    @pytest.mark.django_db
    def test_create_api_permission(self):
        """
        Given a valid set of RBAC permission attributes,
        When an `RBACPermission` object is created,
        Then it should be persisted in the database with the correct string representation.
        """
        # Given / When
        permission = RBACPermission.objects.create(
            name="non-communicable_permission",
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic,
            metric=self.metric,
            geography_type=self.geography_type,
            geography=self.geography,
            age=self.age,
            stratum=self.stratum,
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
    def test_subtheme_must_belong_to_theme(self):
        """
        Given a `SubTheme` associated with a different `Theme`,
        When an `RBACPermission` is created with this subtheme,
        Then an `AdminFormSubthemeAssocThemeError` should be raised.
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
                theme=self.theme,
                sub_theme=invalid_sub_theme,
            ).clean()

    @pytest.mark.django_db
    def test_topic_subtheme_must_have_associated_theme(self):
        """
        Given a `Topic` with a `SubTheme` belonging to a different `Theme`,
        When an `RBACPermission` is created using this topic,
        Then an `AdminFormTopicAssocSubthemeError` should be raised.
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
                theme=self.theme,
                sub_theme=self.sub_theme,
                topic=topic_with_different_theme,
            ).clean()

    @pytest.mark.django_db
    def test_subtheme_must_have_associated_topic(self):
        """
        Given a `SubTheme` without an associated `Topic`,
        When an `RBACPermission` is created using this subtheme,
        Then an `AdminFormSubthemeAssocTopicError` should be raised.
        """
        # Given
        sub_theme_without_topic = SubTheme.objects.create(
            name="mpox-clade-1b", theme=self.theme
        )

        # When / Then
        with pytest.raises(AdminFormSubthemeAssocTopicError):
            RBACPermission(
                name="invalid_subtheme_permission",
                theme=self.theme,
                sub_theme=sub_theme_without_topic,
                topic=self.topic,
            ).clean()

    @pytest.mark.django_db
    def test_duplicate_permission_not_allowed(self):
        """
        Given an existing `RBACPermission` in the database,
        When another `RBACPermission` with the same attributes is created,
        Then an `AdminFormDuplicatePermissionError` should be raised.
        """
        # Given
        RBACPermission.objects.create(
            name="unique_permission",
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic,
            metric=self.metric,
            geography_type=self.geography_type,
            geography=self.geography,
            age=self.age,
            stratum=self.stratum,
        )

        # When / Then
        with pytest.raises(AdminFormDuplicatePermissionError):
            RBACPermission(
                name="duplicate_permission",
                theme=self.theme,
                sub_theme=self.sub_theme,
                topic=self.topic,
                metric=self.metric,
                geography_type=self.geography_type,
                geography=self.geography,
                age=self.age,
                stratum=self.stratum,
            ).clean()
