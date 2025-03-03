import pytest
from unittest import mock
from metrics.data.models.rbac_models import RBACPermission
from metrics.api.packages.permissions import (
    FluentPermissions,
    FluentPermissionsError,
    new_match_dict,
)

MODULE_PATH = "metrics.api.packages.permissions.permissions_fluent"


class TestFluentPermissions:

    data = {
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

    @pytest.fixture
    def fake_rbac_permission(self):
        """Creates a mock RBACPermission object"""
        permission = mock.Mock(spec=RBACPermission)
        permission.theme.name = "infectious_disease"
        permission.sub_theme.name = "respiratory"
        permission.topic.name = "COVID-19"
        permission.metric.name = "COVID-19_cases_casesByDay"
        permission.geography_type.name = "Nation"
        permission.geography.name = "England"
        permission.age.name = "all"
        permission.stratum.name = "default"
        return permission

    def test_add_field_adds_fields_to_list(self):
        """
        Given a FluentPermissions instance
        When add_field() is called multiple times
        Then the fields are added to the internal list
        """
        # Given
        fluent_permissions = FluentPermissions(data={}, group_permissions=[])

        # When
        fluent_permissions.add_field("theme").add_field("sub_theme").add_field("metric")

        # Then
        assert fluent_permissions.field_names == ["theme", "sub_theme", "metric"]

    def test_execute_with_matching_permissions(self, fake_rbac_permission):
        """
        Given a FluentPermissions instance with a matching permission
        When execute() is called
        Then match_fields should correctly reflect matches
        """
        # Given
        fluent_permissions = FluentPermissions(
            data=self.data, group_permissions=[fake_rbac_permission]
        )
        fluent_permissions.add_field("theme").add_field("sub_theme").add_field("topic")

        # When
        fluent_permissions.execute()

        # Then
        expected = {
            "theme": True,
            "sub_theme": True,
            "topic": True,
            "geography_type": False,
            "geography": False,
            "metric": False,
            "age": False,
            "stratum": False,
        }
        assert fluent_permissions._match_fields_all == [expected]

    def test_execute_skips_non_matching_theme_subtheme(self, fake_rbac_permission):
        """
        Given a FluentPermissions instance with a non-matching theme/subtheme
        When execute() is called
        Then the permissions check should be skipped
        """
        # Given
        data = {"theme": "Finance", "sub_theme": "Investment"}
        fluent_permissions = FluentPermissions(
            data=data, group_permissions=[fake_rbac_permission]
        )
        fluent_permissions.add_field("theme").add_field("sub_theme")

        # When
        fluent_permissions.execute()

        # Then
        assert fluent_permissions._match_fields_all == []

    def test_validate_raises_error_when_no_match(self):
        """
        Given a FluentPermissions instance with no matches
        When validate() is called
        Then FluentPermissionsError is raised
        """
        # Given
        fluent_permissions = FluentPermissions(data={}, group_permissions=[])

        # When/Then
        with pytest.raises(FluentPermissionsError):
            fluent_permissions.validate()

    def test_validate_passes_when_match_exists(self, fake_rbac_permission):
        """
        Given a FluentPermissions instance with valid matches
        When validate() is called
        Then no error is raised
        """
        # Given
        fluent_permissions = FluentPermissions(
            data=self.data, group_permissions=[fake_rbac_permission]
        )
        fluent_permissions.add_field("theme").add_field("sub_theme").add_field(
            "topic"
        ).add_field("geography_type").add_field("geography").add_field(
            "metric"
        ).add_field(
            "age"
        ).add_field(
            "stratum"
        ).execute()
        # When/Then
        fluent_permissions.validate()  # Should not raise an exception

    @mock.patch(f"{MODULE_PATH}.MatchFieldAction")
    @mock.patch(f"{MODULE_PATH}.MatchThemeSubThemeFieldsAction")
    def test_execute_calls_correct_actions(
        self, MockThemeSubthemeAction, MockFieldAction, fake_rbac_permission
    ):
        """
        Given a FluentPermissions instance
        When execute() is called
        Then it should invoke the correct action classes
        """
        # Given
        mock_theme_action = MockThemeSubthemeAction.return_value
        mock_field_action = MockFieldAction.return_value
        mock_theme_action.execute.return_value = True
        mock_field_action.execute.return_value = new_match_dict()

        fluent_permissions = FluentPermissions(
            data=self.data, group_permissions=[fake_rbac_permission]
        )
        fluent_permissions.add_field("theme").add_field("sub_theme").add_field(
            "topic"
        ).add_field("geography_type").add_field("geography").add_field(
            "metric"
        ).add_field(
            "age"
        ).add_field(
            "stratum"
        )
        # When
        fluent_permissions.execute()

        # Then
        MockThemeSubthemeAction.assert_called_once_with(data=self.data)
        MockFieldAction.assert_called_once_with(data=self.data)
        mock_theme_action.execute.assert_called()
        mock_field_action.execute.assert_called()
