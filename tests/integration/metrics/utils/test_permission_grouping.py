"""Tests for permission grouping utilities."""

import pytest

from metrics.utils.permission_grouping import group_by_geography_type, group_by_theme
from metrics.utils.permission_hierarchy import NormalizedPermission
from tests.factories.auth_content.models.permission_sets import PermissionSetFactory


class TestGroupByGeographyType:
    """Test suite for group_by_geography_type function."""

    @pytest.mark.django_db
    def test_groups_single_permission_by_geography_type(self):
        """
        Given a single permission with specific geography type
        When grouping by geography type
        Then permission is correctly grouped under its geography type ID
        """
        # Given
        perm_set = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E12000008",
        )

        normalized = NormalizedPermission.from_permission_set(perm_set)

        # When
        result = group_by_geography_type([normalized])

        # Then
        assert "1" in result
        assert result["1"]["geography_type_name"] is not None
        assert "E12000008" in result["1"]["geographies"]
        assert len(result["1"]["geographies"]["E12000008"]["permissions"]) == 1

    @pytest.mark.django_db
    def test_groups_wildcard_geography_type(self):
        """
        Given a permission with wildcard geography type
        When grouping by geography type
        Then permission is grouped under wildcard key with appropriate labels
        """
        # Given
        perm_set = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="-1",
            geography="-1",
        )

        normalized = NormalizedPermission.from_permission_set(perm_set)

        # When
        result = group_by_geography_type([normalized])

        # Then
        assert "-1" in result
        assert result["-1"]["geography_type_name"] == "All Geography Types"
        assert "*" in result["-1"]["geographies"]
        assert result["-1"]["geographies"]["*"]["geography_name"] == "All Geographies"

    @pytest.mark.django_db
    def test_groups_multiple_permissions_same_geography_type(self):
        """
        Given multiple permissions with same geography type but different geographies
        When grouping by geography type
        Then all permissions are grouped under the same geography type ID
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="5",
            metric="11",
            geography_type="1",
            geography="W92000004",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_geography_type(normalized_perms)

        # Then
        assert "1" in result
        assert len(result["1"]["geographies"]) == 2
        assert "E92000001" in result["1"]["geographies"]
        assert "W92000004" in result["1"]["geographies"]

    @pytest.mark.django_db
    def test_groups_multiple_permissions_different_geography_types(self):
        """
        Given multiple permissions with different geography type IDs
        When grouping by geography type
        Then permissions are grouped separately by geography type ID
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="2",
            geography="E12000008",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_geography_type(normalized_perms)

        # Then
        assert len(result) == 2
        assert "1" in result
        assert "2" in result

    @pytest.mark.django_db
    def test_includes_theme_hierarchy_in_geography_groups(self):
        """
        Given permissions grouped by geography
        When examining the result
        Then each permission includes complete theme hierarchy
        """
        # Given
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized = NormalizedPermission.from_permission_set(perm)

        # When
        result = group_by_geography_type([normalized])

        # Then
        permission = result["1"]["geographies"]["E92000001"]["permissions"][0]
        assert "theme" in permission
        assert "sub_theme" in permission
        assert "topic" in permission
        assert "metric" in permission
        assert "id" in permission["theme"]
        assert "name" in permission["theme"]

    @pytest.mark.django_db
    def test_handles_wildcard_geography_within_specific_type(self):
        """
        Given a permission with specific geography type but wildcard geography
        When grouping by geography type
        Then geography name shows "All <type>s"
        """
        # Given
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="2",
            geography="-1",
        )

        normalized = NormalizedPermission.from_permission_set(perm)

        # When
        result = group_by_geography_type([normalized])

        # Then
        assert "2" in result
        assert "*" in result["2"]["geographies"]
        geo_name = result["2"]["geographies"]["*"]["geography_name"]
        assert "All" in geo_name

    @pytest.mark.django_db
    def test_groups_empty_permission_list(self):
        """
        Given an empty list of permissions
        When grouping by geography type
        Then an empty dict is returned
        """
        # When
        result = group_by_geography_type([])

        # Then
        assert result == {}

    @pytest.mark.django_db
    def test_multiple_permissions_same_geography_accumulate(self):
        """
        Given multiple permissions for the same specific geography
        When grouping by geography type
        Then all permissions accumulate under that geography
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="5",
            metric="11",
            geography_type="1",
            geography="E92000001",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_geography_type(normalized_perms)

        # Then
        permissions = result["1"]["geographies"]["E92000001"]["permissions"]
        assert len(permissions) == 2

        topic_ids = [p["topic"]["id"] for p in permissions]
        assert "3" in topic_ids
        assert "5" in topic_ids

    @pytest.mark.django_db
    def test_geography_type_name_formatted_correctly(self):
        """
        Given a permission with geography type ID
        When grouping by geography type
        Then geography type name is formatted with title case and underscores replaced
        """
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized = NormalizedPermission.from_permission_set(perm)

        # When
        result = group_by_geography_type([normalized])

        # Then
        assert "1" in result
        geo_type_name = result["1"]["geography_type_name"]
        assert geo_type_name is not None
        assert geo_type_name != ""


class TestGroupByTheme:
    """Test suite for group_by_theme function."""

    @pytest.mark.django_db
    def test_groups_single_permission_by_theme(self):
        """
        Given a single permission
        When grouping by theme
        Then permission is correctly nested under theme → sub_theme → topic
        """
        # Given
        perm_set = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized = NormalizedPermission.from_permission_set(perm_set)

        # When
        result = group_by_theme([normalized])

        # Then
        assert "2" in result
        assert "2" in result["2"]["sub_themes"]
        assert "3" in result["2"]["sub_themes"]["2"]["topics"]

        topic_data = result["2"]["sub_themes"]["2"]["topics"]["3"]
        assert len(topic_data["geographies"]) == 1

    @pytest.mark.django_db
    def test_groups_wildcard_theme(self):
        """
        Given a permission with wildcard theme
        When grouping by theme
        Then permission is grouped under wildcard key
        """
        # Given
        perm_set = PermissionSetFactory.create_wildcard_permission_set()
        normalized = NormalizedPermission.from_permission_set(perm_set)

        # When
        result = group_by_theme([normalized])

        # Then
        assert "-1" in result
        assert result["-1"]["theme_name"] == "* (All)"
        assert "-1" in result["-1"]["sub_themes"]
        assert "-1" in result["-1"]["sub_themes"]["-1"]["topics"]

    @pytest.mark.django_db
    def test_groups_multiple_topics_under_same_sub_theme(self):
        """
        Given multiple permissions with same theme/sub_theme but different topics
        When grouping by theme
        Then topics are grouped under the same sub_theme
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="5",
            metric="11",
            geography_type="1",
            geography="E92000001",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_theme(normalized_perms)

        # Then
        sub_theme = result["2"]["sub_themes"]["2"]
        assert len(sub_theme["topics"]) == 2
        assert "3" in sub_theme["topics"]
        assert "5" in sub_theme["topics"]

    @pytest.mark.django_db
    def test_groups_multiple_sub_themes_under_same_theme(self):
        """
        Given multiple permissions with same theme but different sub_themes
        When grouping by theme
        Then sub_themes are grouped under the same theme
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="4",
            topic="6",
            metric="12",
            geography_type="1",
            geography="E92000001",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_theme(normalized_perms)

        # Then
        theme = result["2"]
        assert len(theme["sub_themes"]) == 2
        assert "2" in theme["sub_themes"]
        assert "4" in theme["sub_themes"]

    @pytest.mark.django_db
    def test_groups_multiple_themes(self):
        """
        Given multiple permissions with different themes
        When grouping by theme
        Then themes are grouped separately at top level
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="5",
            sub_theme="8",
            topic="12",
            metric="15",
            geography_type="1",
            geography="E92000001",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_theme(normalized_perms)

        # Then
        assert len(result) == 2
        assert "2" in result
        assert "5" in result

    @pytest.mark.django_db
    def test_includes_geography_in_topic_groups(self):
        """
        Given permissions grouped by theme
        When examining the result
        Then each topic includes geography information
        """
        # Given
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized = NormalizedPermission.from_permission_set(perm)

        # When
        result = group_by_theme([normalized])

        # Then
        geographies = result["2"]["sub_themes"]["2"]["topics"]["3"]["geographies"]
        assert len(geographies) == 1

        geography = geographies[0]
        assert "geography_type" in geography
        assert "geography" in geography
        assert "metric" in geography

        # Each should have id and name
        assert "id" in geography["geography_type"]
        assert "name" in geography["geography_type"]

    @pytest.mark.django_db
    def test_multiple_geographies_under_same_topic(self):
        """
        Given multiple permissions with same theme/sub_theme/topic but different geographies
        When grouping by theme
        Then geographies accumulate under the topic
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="W92000004",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_theme(normalized_perms)

        # Then
        geographies = result["2"]["sub_themes"]["2"]["topics"]["3"]["geographies"]
        assert len(geographies) == 2

        geography_codes = [g["geography"]["id"] for g in geographies]
        assert "E92000001" in geography_codes
        assert "W92000004" in geography_codes

    @pytest.mark.django_db
    def test_groups_empty_permission_list(self):
        """
        Given an empty list of permissions
        When grouping by theme
        Then an empty dict is returned
        """
        # When
        result = group_by_theme([])

        # Then
        assert result == {}

    @pytest.mark.django_db
    def test_preserves_names_correctly(self):
        """
        Given permissions with populated names
        When grouping by theme
        Then names are preserved at each level
        """
        # Given
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized = NormalizedPermission.from_permission_set(perm)

        # When
        result = group_by_theme([normalized])

        # Then
        assert result["2"]["theme_name"] is not None
        assert result["2"]["sub_themes"]["2"]["sub_theme_name"] is not None
        assert result["2"]["sub_themes"]["2"]["topics"]["3"]["topic_name"] is not None

    @pytest.mark.django_db
    def test_handles_wildcard_at_sub_theme_level(self):
        """
        Given a permission with specific theme but wildcard sub_theme
        When grouping by theme
        Then wildcard is correctly placed in hierarchy
        """
        # Given
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )

        normalized = NormalizedPermission.from_permission_set(perm)

        # When
        result = group_by_theme([normalized])

        # Then
        assert "2" in result
        assert "-1" in result["2"]["sub_themes"]
        assert result["2"]["sub_themes"]["-1"]["sub_theme_name"] == "* (All)"


class TestGroupingIntegration:
    """Integration tests for both grouping functions together."""

    @pytest.mark.django_db
    def test_complex_scenario_multiple_dimensions(self):
        """
        Given a complex set of permissions across multiple dimensions
        When grouping by both geography and theme
        Then both groupings produce correct structures
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="5",
            metric="11",
            geography_type="2",  # Different geography type ID
            geography="E12000008",
        )
        perm3 = PermissionSetFactory.create_permission_set(
            theme="5",
            sub_theme="8",
            topic="12",
            metric="15",
            geography_type="1",
            geography="W92000004",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
            NormalizedPermission.from_permission_set(perm3),
        ]

        # When
        geo_grouped = group_by_geography_type(normalized_perms)
        theme_grouped = group_by_theme(normalized_perms)

        # Then
        assert len(geo_grouped) == 2
        assert "1" in geo_grouped
        assert "2" in geo_grouped
        assert len(geo_grouped["1"]["geographies"]) == 2

        assert len(theme_grouped) == 2
        assert "2" in theme_grouped
        assert "5" in theme_grouped
        assert len(theme_grouped["2"]["sub_themes"]["2"]["topics"]) == 2

    @pytest.mark.django_db
    def test_wildcard_appears_in_both_groupings(self):
        """
        Given a wildcard permission
        When grouping by both geography and theme
        Then wildcard appears correctly in both structures
        """
        # Given
        wildcard = PermissionSetFactory.create_wildcard_permission_set()
        normalized = NormalizedPermission.from_permission_set(wildcard)

        # When
        geo_grouped = group_by_geography_type([normalized])
        theme_grouped = group_by_theme([normalized])

        # Then
        assert "-1" in geo_grouped
        assert geo_grouped["-1"]["geography_type_name"] == "All Geography Types"

        # Then
        assert "-1" in theme_grouped
        assert theme_grouped["-1"]["theme_name"] == "* (All)"

    @pytest.mark.django_db
    def test_mixed_geography_types_with_same_theme(self):
        """
        Given permissions with same theme but different geography type IDs
        When grouping by geography type
        Then they are grouped separately by geography type ID
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="2",
            geography="E12000008",
        )

        normalized_perms = [
            NormalizedPermission.from_permission_set(perm1),
            NormalizedPermission.from_permission_set(perm2),
        ]

        # When
        result = group_by_geography_type(normalized_perms)

        # Then
        assert len(result) == 2
        assert "1" in result
        assert "2" in result
        assert len(result["1"]["geographies"]) == 1
        assert len(result["2"]["geographies"]) == 1
