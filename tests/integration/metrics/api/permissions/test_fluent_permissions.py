import pytest
from metrics.api.permissions.fluent_permissions import (
    FluentPermissions,
)
from metrics.api.permissions.fluent_permissions import RequestedDataParameters
from tests.fakes.factories.metrics.rbac_models.rbac_permission import (
    FakeRBACPermissionFactory,
)

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


class TestFluentPermissions:
    def test_check_permission_allows_access_validates_for_exact_fine_grained_permission(
        self,
    ):
        """
        Given a requested set of parameters
        And an `RBACPermission` which specifies the exact requested dataset
        When `check_permission_allows_access()` is called
            from an instance of `FluentPermissions`
        Then True is returned
        """
        # Given
        requested_data_parameters = RequestedDataParameters(**DATA_PARAMETERS)
        fluent_permissions = FluentPermissions(
            requested_data_parameters=requested_data_parameters
        )
        fake_exact_matching_rbac_permission = (
            FakeRBACPermissionFactory.build_rbac_permission(
                theme=DATA_PARAMETERS["theme"],
                sub_theme=DATA_PARAMETERS["sub_theme"],
                topic=DATA_PARAMETERS["topic"],
                metric=DATA_PARAMETERS["metric"],
                geography=DATA_PARAMETERS["geography"],
                geography_type=DATA_PARAMETERS["geography_type"],
            )
        )

        # When
        is_access_allowed: bool = fluent_permissions.check_permission_allows_access(
            rbac_permission=fake_exact_matching_rbac_permission
        )

        # Then
        assert is_access_allowed

    @pytest.mark.parametrize(
        "matching_fields",
        (
            # Show all data for `infectious_disease`
            {
                "theme",
            },
            # Show all data for `infectious_disease` `respiratory`
            {
                "theme",
                "sub_theme",
            },
            # Show all data for `COVID-19`
            {
                "theme",
                "sub_theme",
                "topic",
            },
            # Show all data for `COVID-19_cases_casesByDay`
            {
                "theme",
                "sub_theme",
                "topic",
                "metric",
            },
            # Show all data under the `Nation` geography type scope
            {
                "geography_type",
            },
            # Show for all data in `England`
            {
                "geography_type",
                "geography",
            },
            # Show all data for `COVID-19_cases_casesByDay` in `England`
            {
                "theme",
                "sub_theme",
                "topic",
                "metric",
                "geography",
                "geography_type",
            },
            # Show all data for `COVID-19` in `England
            {
                "theme",
                "sub_theme",
                "topic",
                "geography",
                "geography_type",
            },
        ),
    )
    def test_check_permission_allows_access_validates_for_wildcard_permissions_with_enough_of_a_match(
        self, matching_fields: set[str]
    ):
        """
        Given a requested set of parameters
        And an `RBACPermission` which specifies enough of the parameters
            to incur a wildcard match
        When `check_permission_allows_access()` is called
            from an instance of `FluentPermissions`
        Then True is returned
        """
        # Given
        requested_data_parameters = RequestedDataParameters(**DATA_PARAMETERS)
        fluent_permissions = FluentPermissions(
            requested_data_parameters=requested_data_parameters
        )

        permission_values = {
            k: v for k, v in DATA_PARAMETERS.items() if k in matching_fields
        }
        fake_rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            **permission_values
        )

        # When
        is_access_allowed: bool = fluent_permissions.check_permission_allows_access(
            rbac_permission=fake_rbac_permission
        )

        # Then
        assert is_access_allowed

    @pytest.mark.parametrize(
        "permission_values",
        (
            # Permission for data for a different theme i.e. `extreme_event` instead of `infectious_disease`
            {
                "theme": "extreme_event",
            },
            # Permission for data for a different sub_theme i.e. `vaccine_preventable` instead of `respiratory`
            {
                "theme": DATA_PARAMETERS["theme"],
                "sub_theme": "vaccine_preventable",
            },
            # Permission for data for a different topic i.e. `RSV` instead of `COVID-19`
            {
                "theme": DATA_PARAMETERS["theme"],
                "sub_theme": DATA_PARAMETERS["sub_theme"],
                "topic": "RSV",
            },
            # Permission for data for a different metric i.e. `COVID-19_vaccinations_autumn22_dosesByDay`
            {
                "theme": DATA_PARAMETERS["theme"],
                "sub_theme": DATA_PARAMETERS["sub_theme"],
                "topic": DATA_PARAMETERS["topic"],
                "metric": "COVID-19_vaccinations_autumn22_dosesByDay",
            },
            # Permission for data for a different geography_type i.e. `Lower Tier Local Authority` instead of `Nation`
            {
                "geography_type": "Lower Tier Local Authority",
            },
            # Permission for data a different geography i.e. `Wales` instead of `England`
            {
                "geography_type": DATA_PARAMETERS["geography_type"],
                "geography": "Wales",
            },
            # Permission for data a different geography but with the same metric i.e. `Wales` instead of `England`
            {
                "theme": DATA_PARAMETERS["theme"],
                "sub_theme": DATA_PARAMETERS["sub_theme"],
                "topic": DATA_PARAMETERS["topic"],
                "metric": DATA_PARAMETERS["metric"],
                "geography": "Wales",
                "geography_type": DATA_PARAMETERS["geography_type"],
            },
            # Permission for data a different geography but with the same topic i.e. `Wales` instead of `England`
            {
                "theme": DATA_PARAMETERS["theme"],
                "sub_theme": DATA_PARAMETERS["sub_theme"],
                "topic": DATA_PARAMETERS["topic"],
                "geography": "Wales",
                "geography_type": DATA_PARAMETERS["geography_type"],
            },
        ),
    )
    def test_check_permission_allows_access_invalidates_for_permissions_without_match(
        self, permission_values: dict[str, str]
    ):
        """
        Given a requested set of parameters
        And an `RBACPermission` which specifies parameters
            resulting in a wildcard mismatch
        When `check_permission_allows_access()` is called
            from an instance of `FluentPermissions`
        Then False is returned
        """
        # Given
        requested_data_parameters = RequestedDataParameters(**DATA_PARAMETERS)
        fluent_permissions = FluentPermissions(
            requested_data_parameters=requested_data_parameters
        )

        fake_rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            **permission_values
        )

        # When
        is_access_allowed: bool = fluent_permissions.check_permission_allows_access(
            rbac_permission=fake_rbac_permission
        )

        # Then
        assert not is_access_allowed

    def test_check_permission_allows_access_invalidates_for_non_matching_wildcard_permission(
        self,
    ):
        """
        Given a requested set of parameters
        And an `RBACPermission` which specifies a different theme and sub_theme
        When `check_permission_allows_access()` is called
            from an instance of `FluentPermissions`
        Then False is returned
        """
        # Given
        requested_data_parameters = RequestedDataParameters(**DATA_PARAMETERS)
        fluent_permissions = FluentPermissions(
            requested_data_parameters=requested_data_parameters
        )
        fake_rbac_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="extreme_event",
            sub_theme="weather_alert",
        )

        # When
        is_access_allowed: bool = fluent_permissions.check_permission_allows_access(
            rbac_permission=fake_rbac_permission
        )

        # Then
        assert not is_access_allowed

    def test_check_if_any_permissions_allow_access_validates_correctly(self):
        """
        Given a requested set of parameters
        And a number of `RBACPermission` models
            one of which provides a match
        When `check_if_any_permissions_allow_access()` is called
            from an instance of `FluentPermissions`
        Then True is returned
        """
        # Given
        requested_data_parameters = RequestedDataParameters(**DATA_PARAMETERS)
        fluent_permissions = FluentPermissions(
            requested_data_parameters=requested_data_parameters
        )
        non_matching_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="extreme_event",
            sub_theme="weather_alert",
        )
        matching_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme=DATA_PARAMETERS["theme"],
            sub_theme=DATA_PARAMETERS["sub_theme"],
        )

        # When
        is_access_allowed: bool = (
            fluent_permissions.check_if_any_permissions_allow_access(
                rbac_permissions=[non_matching_permission, matching_permission]
            )
        )

        # Then
        assert is_access_allowed

    def test_check_if_any_permissions_allow_access_invalidates_correctly(self):
        """
        Given a requested set of parameters
        And a number of `RBACPermission` models
            none of which provide any match
        When `check_if_any_permissions_allow_access()` is called
            from an instance of `FluentPermissions`
        Then False is returned
        """
        # Given
        requested_data_parameters = RequestedDataParameters(**DATA_PARAMETERS)
        fluent_permissions = FluentPermissions(
            requested_data_parameters=requested_data_parameters
        )
        non_matching_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme="extreme_event",
            sub_theme="weather_alert",
        )
        other_non_matching_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme=DATA_PARAMETERS["theme"],
            sub_theme=DATA_PARAMETERS["sub_theme"],
            topic="RSV",
        )

        # When
        is_access_allowed: bool = (
            fluent_permissions.check_if_any_permissions_allow_access(
                rbac_permissions=[
                    non_matching_permission,
                    other_non_matching_permission,
                ]
            )
        )

        # Then
        assert not is_access_allowed
