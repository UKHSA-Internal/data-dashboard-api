import pytest
from unittest import mock
from metrics.api.packages.permissions import (
    FluentPermissions,
    FluentPermissionsError,
    new_match_dict,
)
from tests.fakes.factories.metrics.rbac_models.rbac_permission import (
    FakeRBACPermissionFactory,
)
from tests.fakes.models.metrics.rbac_models.rbac_permission import FakeRBACPermission

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
    def fake_rbac_permission(self) -> FakeRBACPermission:
        """Creates a fake RBACPermission object"""
        return FakeRBACPermissionFactory.build_rbac_permission(
            theme_name=self.data["theme"],
            sub_theme_name=self.data["sub_theme"],
            topic_name=self.data["topic"],
            metric_name=self.data["metric"],
            geography_name=self.data["geography"],
            geography_type_name=self.data["geography_type"],
            age_name=self.data["age"],
            stratum_name=self.data["stratum"],
        )

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

    def test_execute_with_matching_permissions(
        self, fake_rbac_permission: FakeRBACPermission
    ):
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

    def test_execute_skips_non_matching_theme_subtheme(
        self, fake_rbac_permission: FakeRBACPermission
    ):
        """
        Given a FluentPermissions instance with a non-matching theme/subtheme
        When execute() is called
        Then the permissions check should be skipped
        """
        # Given
        data = {"theme": "extreme_event", "sub_theme": "weather_alert"}
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

    def test_validate_raises_error_when_permission_cannot_be_matched(self):
        """
        Given a FluentPermissions instance
            with a permission for a different dataset
        When validate() is called
        Then a `FluentPermissionsError` is raised
        """
        # Given
        non_matching_permission = FakeRBACPermissionFactory.build_rbac_permission(
            theme_name="extreme_event",
            sub_theme_name="weather_alert",
        )
        requested_data = {
            "theme": "infectious_disease",
            "sub_theme": "respiratory",
        }

        fluent_permissions = FluentPermissions(
            data=requested_data, group_permissions=[non_matching_permission]
        )

        # When/Then
        with pytest.raises(FluentPermissionsError):
            fluent_permissions.validate()

    def test_validate_passes_when_match_exists(
        self, fake_rbac_permission: FakeRBACPermission
    ):
        """
        Given a FluentPermissions instance with valid matches
        When validate() is called
        Then no error is raised
        """
        # Given
        fluent_permissions = FluentPermissions(
            data=self.data, group_permissions=[fake_rbac_permission]
        )
        (
            fluent_permissions.add_field("theme")
            .add_field("sub_theme")
            .add_field("topic")
            .add_field("geography_type")
            .add_field("geography")
            .add_field("metric")
            .add_field("age")
            .add_field("stratum")
            .execute()
        )
        # When/Then
        fluent_permissions.validate()  # Should not raise an exception

    def test_validate_passes_when_wildcard_permission_matches_requested_dataset(
        self, fake_rbac_permission: FakeRBACPermission
    ):
        """
        Given a FluentPermissions instance
            with an `RBACPPermission` which wildcards the dataset
        When validate() is called
        Then no error is raised
        """
        # Given
        wildcarded_permission = fake_rbac_permission
        wildcarded_permission.metric = None
        wildcarded_permission.topic = None
        wildcarded_permission.age = None
        wildcarded_permission.geography = None
        # Permission wildcards for the selected theme & sub_theme

        fluent_permissions = FluentPermissions(
            data=self.data, group_permissions=[fake_rbac_permission]
        )
        (
            fluent_permissions.add_field("theme")
            .add_field("sub_theme")
            .add_field("topic")
            .add_field("geography_type")
            .add_field("geography")
            .add_field("metric")
            .add_field("age")
            .add_field("stratum")
            .execute()
        )
        # When/Then
        fluent_permissions.validate()  # Should not raise an exception

    @mock.patch(f"{MODULE_PATH}.MatchFieldAction")
    @mock.patch(f"{MODULE_PATH}.MatchThemeSubThemeFieldsAction")
    def test_execute_calls_correct_actions(
        self,
        mocked_theme_subtheme_action: mock.MagicMock,
        mocked_field_action: mock.MagicMock,
        fake_rbac_permission: FakeRBACPermission,
    ):
        """
        Given a FluentPermissions instance
        When execute() is called
        Then it should invoke the correct action classes
        """
        # Given
        mock_theme_action = mocked_theme_subtheme_action.return_value
        mock_field_action = mocked_field_action.return_value
        mock_theme_action.execute.return_value = True
        mock_field_action.execute.return_value = new_match_dict()

        fluent_permissions = FluentPermissions(
            data=self.data, group_permissions=[fake_rbac_permission]
        )
        (
            fluent_permissions.add_field("theme")
            .add_field("sub_theme")
            .add_field("topic")
            .add_field("geography_type")
            .add_field("geography")
            .add_field("metric")
            .add_field("age")
            .add_field("stratum")
        )
        # When
        fluent_permissions.execute()

        # Then
        mocked_theme_subtheme_action.assert_called_once_with(data=self.data)
        mocked_field_action.assert_called_once_with(data=self.data)
        mock_theme_action.execute.assert_called()
        mock_field_action.execute.assert_called()

    def test_match_fields_all_property(self):
        """
        Given a FluentPermissions instance
        When match_fields_all is accessed
        Then it should return the stored _match_fields_all data
        """
        # Given
        fluent_permissions = FluentPermissions(data={}, group_permissions=[])
        fluent_permissions._match_fields_all = [new_match_dict()]

        # When
        result = fluent_permissions.match_fields_all

        # Then
        assert result == [new_match_dict()]

    @pytest.mark.parametrize(
        "data",
        [
            {"theme": "infectious_disease"},
            {"sub_theme": "respiratory"},
            {},
        ],
    )
    def test_match_theme_sub_theme_returns_false_when_keys_missing(
        self,
        fake_rbac_permission: FakeRBACPermission,
        data: dict[str, str],
    ):
        """
        Given a FluentPermissions instance
        When _match_theme_sub_theme() is called with missing theme or sub_theme
        Then it should return False
        """
        # Given
        fluent_permissions = FluentPermissions(
            data=data, group_permissions=[fake_rbac_permission]
        )

        # When
        result = fluent_permissions._match_theme_sub_theme(fake_rbac_permission)

        # Then
        assert result is False
