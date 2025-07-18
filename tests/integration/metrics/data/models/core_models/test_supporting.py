import django.db.utils
import pytest

from metrics.data.models.core_models import (
    Age,
    Geography,
    GeographyType,
    Metric,
    MetricGroup,
    Stratum,
    SubTheme,
    Theme,
    Topic,
)


class TestSupportingCoreModelsQuerySets:
    @pytest.mark.django_db
    def test_theme_queryset_returns_all_names(self):
        """
        Given an instance of the ThemeModel's `ThemeQuerySet`
        When `get_all_names()` is called
        Then it should return all available names.
        """
        # Given
        fake_theme_name_one = "infectious_disease"
        fake_theme_name_two = "extreme_event"
        Theme.objects.create(name=fake_theme_name_one)
        Theme.objects.create(name=fake_theme_name_two)

        # When / Then
        assert Theme.objects.all().count() == Theme.objects.get_all_names().count()

    @pytest.mark.django_db
    def test_sub_theme_queryset_returns_all_names(self):
        """
        Given an instance of the SubThemeModel's `SubThemeQuerySet`
        When `get_all_names()` is called
        Then it should return all available names.
        """
        # Given
        fake_sub_theme_name_one = "respiratory"
        fake_sub_theme_name_two = "weather_alert"
        SubTheme.objects.create(name=fake_sub_theme_name_one)
        SubTheme.objects.create(name=fake_sub_theme_name_two)

        # When / Then
        assert (
            SubTheme.objects.all().count() == SubTheme.objects.get_all_names().count()
        )


class TestSupportingCoreModels:
    @pytest.mark.django_db
    def test_theme_models_remain_unique(self):
        """
        Given a name for an existing `Theme` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        name = "infectious_disease"
        Theme.objects.create(name=name)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            Theme.objects.create(name=name)

    @pytest.mark.django_db
    def test_sub_theme_models_remain_unique(self):
        """
        Given a name for an existing `SubTheme` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        theme = Theme.objects.create(name="infectious_disease")

        name = "respiratory"
        SubTheme.objects.create(name=name, theme=theme)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            SubTheme.objects.create(name=name, theme=theme)

    @pytest.mark.django_db
    def test_topic_models_remain_unique(self):
        """
        Given a name for an existing `Topic` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        sub_theme = SubTheme.objects.create(name="respiratory")
        name = "COVID-19"
        Topic.objects.create(name=name, sub_theme=sub_theme)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            Topic.objects.create(name=name, sub_theme=sub_theme)

    @pytest.mark.django_db
    def test_topic_models_with_different_sub_themes_are_allowed(self):
        """
        Given a name for an existing `Topic` record
        When another record is attempted to be created with the same name
            but a different subtheme
        Then this is allowed
        """
        # Given
        sub_theme_respiratory = SubTheme.objects.create(name="respiratory")
        sub_theme_cardiovascular = SubTheme.objects.create(name="cardiovascular")

        name = "COVID-19"
        Topic.objects.create(name=name, sub_theme=sub_theme_respiratory)

        # When / Then
        Topic.objects.create(name=name, sub_theme=sub_theme_cardiovascular)

    @pytest.mark.django_db
    def test_metric_group_models_remain_unique(self):
        """
        Given a name for an existing `MetricGroup` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        topic = Topic.objects.create(name="COVID-19")
        name = "cases"
        MetricGroup.objects.create(name=name, topic=topic)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            MetricGroup.objects.create(name=name, topic=topic)

    @pytest.mark.django_db
    def test_metric_models_remain_unique(self):
        """
        Given a name for an existing `Metric` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        topic = Topic.objects.create(name="COVID-19")
        name = "COVID-19_cases_countRollingMean"
        Metric.objects.create(name=name, topic=topic)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            Metric.objects.create(name=name, topic=topic)

    @pytest.mark.django_db
    def test_geography_type_models_remain_unique(self):
        """
        Given a name for an existing `GeographyType` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        name = "Nation"
        GeographyType.objects.create(name=name)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            GeographyType.objects.create(name=name)

    @pytest.mark.django_db
    def test_geography_models_remain_unique(self):
        """
        Given a name for an existing `Geography` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        geography_type = GeographyType.objects.create(name="Nation")
        name = "London"
        Geography.objects.create(name=name, geography_type=geography_type)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            Geography.objects.create(name=name, geography_type=geography_type)

    @pytest.mark.django_db
    def test_geography_models_with_same_names_but_different_types_are_allowed(self):
        """
        Given a name which is shared between two `Geography` records
             but with different `GeographyTypes`
        When the 2 records are created
        Then the records are persisted and the unique constraints are satisfied
        """
        # Given
        shared_name = "London"
        geography_type_one = GeographyType.objects.create(
            name="Upper Tier Local Authority"
        )
        geography_type_two = GeographyType.objects.create(
            name="Lower Tier Local Authority"
        )

        # When
        Geography.objects.create(name=shared_name, geography_type=geography_type_one)
        Geography.objects.create(name=shared_name, geography_type=geography_type_two)

        # Then
        assert Geography.objects.all().count() == 2

    @pytest.mark.django_db
    def test_stratum_models_remain_unique(self):
        """
        Given a name for an existing `Stratum` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        name = "Pillar A"
        Stratum.objects.create(name=name)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            Stratum.objects.create(name=name)

    @pytest.mark.django_db
    def test_age_models_remain_unique(self):
        """
        Given a name for an existing `Age` record
        When another record is attempted to be created with the same name
        Then an `IntegrityError` is raised
        """
        # Given
        name = "80+"
        Age.objects.create(name=name)

        # When / Then
        with pytest.raises(django.db.utils.IntegrityError):
            Age.objects.create(name=name)
