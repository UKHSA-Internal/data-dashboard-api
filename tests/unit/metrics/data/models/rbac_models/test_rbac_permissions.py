from unittest import mock

import pytest

from metrics.data.models import RBACPermission
from metrics.data.models.rbac_models.rbac_permissions import (
    NoModelSelectedError,
    SelectionInvalidWithParentSelectionError,
    NoSelectionMadeError,
)
from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.rbac_models.rbac_permission import (
    FakeRBACPermissionFactory,
)
from tests.fakes.factories.metrics.sub_theme_factory import FakeSubThemeFactory
from tests.fakes.factories.metrics.theme_factory import FakeThemeFactory
from tests.fakes.factories.metrics.topic_factory import FakeTopicFactory

DATA_PARAMETERS = {
    "theme": "infectious_disease",
    "sub_theme": "respiratory",
    "topic": "COVID-19",
    "metric": "COVID-19_cases_casesByDay",
    "geography": "England",
    "geography_type": "Nation",
    "sex": "all",
    "age": "all",
    "stratum": "default",
}


class TestRBACPermission:
    @pytest.fixture(autouse=True, scope="class")
    def stubbed_rbac_duplicate_permission_check(self):
        with mock.patch.object(
            RBACPermission, "_check_rbac_permissions_exist"
        ) as mocked:
            yield mocked

    @pytest.mark.parametrize(
        "included_fields",
        (
            {
                "theme",
            },
            {
                "theme",
                "sub_theme",
            },
            {
                "theme",
                "sub_theme",
                "topic",
            },
            {
                "theme",
                "sub_theme",
                "topic",
                "metric",
            },
            {
                "geography_type",
            },
            {
                "geography_type",
                "geography",
            },
            {
                "theme",
                "sub_theme",
                "topic",
                "metric",
                "geography",
                "geography_type",
            },
            {
                "theme",
                "sub_theme",
                "topic",
                "geography",
                "geography_type",
            },
        ),
    )
    def test_selection_validation_passes_successfully(self, included_fields: set[str]):
        """
        Given a set of valid selections
        When `clean()` is called from an instance
            of `RBACPermission`
        Then the check is validated successfully
        """
        # Given
        permission_values = {
            k: v for k, v in DATA_PARAMETERS.items() if k in included_fields
        }
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            **permission_values
        )

        # When / Then
        rbac_permission.clean()

    def test_sub_theme_selection_is_invalidated_for_different_theme(self):
        """
        Given a selected sub theme for a different theme
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `SelectionInvalidWithParentSelectionError` is raised
        """
        # Given
        fake_theme = FakeThemeFactory.build_example_theme(name="extreme_event")
        fake_sub_theme = FakeSubThemeFactory.build_example_sub_theme(
            name="weather_alert", theme=fake_theme
        )
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="infectious_disease",
        )
        rbac_permission.sub_theme = fake_sub_theme

        # When / Then
        with pytest.raises(SelectionInvalidWithParentSelectionError):
            rbac_permission.clean()

    def test_topic_selection_is_invalidated_for_different_sub_theme(self):
        """
        Given a selected topic for a different sub theme
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `SelectionInvalidWithParentSelectionError` is raised
        """
        # Given
        fake_theme = FakeThemeFactory.build_example_theme(name="extreme_event")
        fake_sub_theme = FakeSubThemeFactory.build_example_sub_theme(
            name="weather_alert", theme=fake_theme
        )
        fake_topic = FakeTopicFactory.build_example_topic(
            name="COVID-19", sub_theme=fake_sub_theme
        )
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="infectious_disease",
            sub_theme="respiratory",
        )
        rbac_permission.topic = fake_topic

        # When / Then
        with pytest.raises(SelectionInvalidWithParentSelectionError):
            rbac_permission.clean()

    def test_topic_selection_is_invalidated_for_no_sub_theme(self):
        """
        Given a selected topic without a selected sub theme
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `NoModelSelectedError` is raised
        """
        # Given
        fake_theme = FakeThemeFactory.build_example_theme(name="extreme_event")
        fake_sub_theme = FakeSubThemeFactory.build_example_sub_theme(
            name="respiratory", theme=fake_theme
        )
        fake_topic = FakeTopicFactory.build_example_topic(
            name="COVID-19", sub_theme=fake_sub_theme
        )
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="infectious_disease",
        )
        rbac_permission.topic = fake_topic

        # When / Then
        with pytest.raises(NoModelSelectedError):
            rbac_permission.clean()

    def test_metric_selection_is_invalidated_for_different_topic(self):
        """
        Given a selected metric for a different topic
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `SelectionInvalidWithParentSelectionError` is raised
        """
        # Given
        fake_metric = FakeMetricFactory.build_example_metric(
            theme_name="infectious_disease",
            sub_theme_name="respiratory",
            topic_name="hMPV",
            metric_name="hMPV_testing_positivityByWeek",
        )
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="infectious_disease", sub_theme="respiratory", topic="COVID-19"
        )
        rbac_permission.metric = fake_metric

        # When / Then
        with pytest.raises(SelectionInvalidWithParentSelectionError):
            rbac_permission.clean()

    def test_metric_selection_is_invalidated_for_no_topic(self):
        """
        Given a selected metric without a selected topic
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `NoModelSelectedError` is raised
        """
        # Given
        fake_metric = FakeMetricFactory.build_example_metric(
            theme_name="infectious_disease",
            sub_theme_name="respiratory",
            topic_name="hMPV",
            metric_name="hMPV_testing_positivityByWeek",
        )
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="infectious_disease",
            sub_theme="respiratory",
        )
        rbac_permission.metric = fake_metric

        # When / Then
        with pytest.raises(NoModelSelectedError):
            rbac_permission.clean()

    def test_geography_selection_is_invalidated_for_different_geography_type(self):
        """
        Given
        When
        Then
        """
        # Given
        fake_geography = FakeGeographyFactory.build_example(
            geography_name="Bolsover",
            geography_type_name="Lower Tier Local Authority",
        )

        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            geography_type="Nation",
            geography="England",
        )
        rbac_permission.geography = fake_geography

        # When / Then
        with pytest.raises(SelectionInvalidWithParentSelectionError):
            rbac_permission.clean()

    def test_geography_selection_is_invalidated_for_no_geography_type(self):
        """
        Given a selected geography without a selected geography type
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `NoModelSelectedError` is raised
        """
        # Given
        fake_geography = FakeGeographyFactory.build_example(
            geography_name="England",
            geography_type_name="Nation",
        )

        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission()
        rbac_permission.geography = fake_geography

        # When / Then
        with pytest.raises(NoModelSelectedError):
            rbac_permission.clean()

    def test_complete_wildcard_selection_is_invalidated(self):
        """
        Given no selection i.e. a complete wildcard
            which would give complete access
        When `clean()` is called from an instance
            of `RBACPermission`
        Then a `NoSelectionMadeError` is raised
        """
        # Given
        rbac_permission = FakeRBACPermissionFactory.build_rbac_permission()

        # When / Then
        with pytest.raises(NoSelectionMadeError):
            rbac_permission.clean()
