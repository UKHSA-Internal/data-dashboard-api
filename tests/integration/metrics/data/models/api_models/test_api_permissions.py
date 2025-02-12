import pytest

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
from metrics.data.models.api_models.api_permissions import (
    AdminFormSubthemeAssocThemeError,
    AdminFormTopicAssocSubthemeError,
    AdminFormSubthemeAssocTopicError,
    AdminFormDuplicatePermissionError,
    ApiPermission,
)


class TestApiPermission:
    @pytest.fixture(autouse=True)
    def setup(self, db):
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
        permission = ApiPermission.objects.create(
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
        assert ApiPermission.objects.count() == 1
        assert str(permission) == (
            "name=non-communicable_permission, "
            "theme=non-communicable, "
            "sub_theme=respiratory, "
            "topic=asthma, "
            "metric=asthma_syndromic_emergencyDepartment_countsByDay, "
            "geography_type=Nation, "
            "geography=England, "
            "age=England, "
            "stratum=default"
        )

    @pytest.mark.django_db
    def test_subtheme_must_belong_to_theme(self):
        other_theme = Theme.objects.create(name="infectious_disease")
        invalid_sub_theme = SubTheme.objects.create(
            name="weather_alert", theme=other_theme
        )

        with pytest.raises(AdminFormSubthemeAssocThemeError):
            ApiPermission(
                name="invalid_permission",
                theme=self.theme,
                sub_theme=invalid_sub_theme,
            ).clean()

    @pytest.mark.django_db
    def test_topic_subtheme_must_have_associated_theme(self):
        other_theme = Theme.objects.create(name="infectious_disease")
        other_sub_theme = SubTheme.objects.create(name="respiratory", theme=other_theme)
        topic_with_different_theme = Topic.objects.create(
            name="E-coli", sub_theme=other_sub_theme
        )

        with pytest.raises(AdminFormTopicAssocSubthemeError):
            ApiPermission(
                name="invalid_topic_permission",
                theme=self.theme,
                sub_theme=self.sub_theme,
                topic=topic_with_different_theme,
            ).clean()

    @pytest.mark.django_db
    def test_subtheme_must_have_associated_topic(self):
        sub_theme_without_topic = SubTheme.objects.create(
            name="mpox-clade-1b", theme=self.theme
        )

        with pytest.raises(AdminFormSubthemeAssocTopicError):
            ApiPermission(
                name="invalid_subtheme_permission",
                theme=self.theme,
                sub_theme=sub_theme_without_topic,
                topic=self.topic,
            ).clean()

    @pytest.mark.django_db
    def test_duplicate_permission_not_allowed(self):
        ApiPermission.objects.create(
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

        with pytest.raises(AdminFormDuplicatePermissionError):
            ApiPermission(
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
