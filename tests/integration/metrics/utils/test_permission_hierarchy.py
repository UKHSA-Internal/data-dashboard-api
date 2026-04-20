"""Tests for permission hierarchy utilities."""

from uuid import uuid4

import pytest

from metrics.utils.permission_hierarchy import (
    NormalizedPermission,
    _get_choice_label,
    build_permission_hierarchy,
    get_deduplicated_permissions,
)
from tests.factories.auth_content.models.permission_sets import PermissionSetFactory
from tests.factories.metrics.theme import ThemeFactory


class TestNormalizedPermission:
    """Test suite for NormalizedPermission dataclass."""

    @pytest.mark.django_db
    def test_from_permission_set_creates_normalized_permission(self):
        """
        Given a PermissionSet instance
        When creating a NormalizedPermission from it
        Then all IDs are correctly extracted
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

        # When
        normalized = NormalizedPermission.from_permission_set(perm_set)

        # Then
        assert normalized.theme_id == "2"
        assert normalized.sub_theme_id == "2"
        assert normalized.topic_id == "3"
        assert normalized.metric_id == "10"
        assert normalized.geography_type_id == "1"
        assert normalized.geography_id == "E92000001"

    @pytest.mark.django_db
    def test_from_permission_set_populates_names(self):
        """
        Given a PermissionSet instance
        When creating a NormalizedPermission from it
        Then all names are populated via database lookups
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

        # When
        normalized = NormalizedPermission.from_permission_set(perm_set)

        # Then
        assert normalized.theme_name != ""
        assert normalized.sub_theme_name != ""
        assert normalized.topic_name != ""
        assert normalized.metric_name != ""
        assert normalized.geography_type_name != ""
        assert normalized.geography_name != ""

    @pytest.mark.django_db
    def test_from_permission_set_handles_wildcards(self):
        """
        Given a PermissionSet with wildcard values
        When creating a NormalizedPermission from it
        Then wildcard IDs are "-1" and names are "* (All)"
        """
        # Given
        wildcard_perm = PermissionSetFactory.create_wildcard_permission_set()

        # When
        normalized = NormalizedPermission.from_permission_set(wildcard_perm)

        # Then
        assert normalized.theme_id == "-1"
        assert normalized.theme_name == "* (All)"
        assert normalized.sub_theme_id == "-1"
        assert normalized.sub_theme_name == "* (All)"
        assert normalized.topic_id == "-1"
        assert normalized.topic_name == "* (All)"
        assert normalized.metric_id == "-1"
        assert normalized.metric_name == "* (All)"
        assert normalized.geography_type_id == "-1"
        assert normalized.geography_type_name == "* (All)"
        assert normalized.geography_id == "-1"
        assert normalized.geography_name == "* (All)"

    @pytest.mark.django_db
    def test_from_permission_set_handles_empty_values(self):
        """
        Given a PermissionSet with some empty values, which can't really happen due to the model and the validation.
        When creating a NormalizedPermission from it
        Then empty values become empty strings
        """
        # Given
        perm_set = PermissionSetFactory.create(
            theme="2",
            sub_theme="",
            topic="",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        # When
        normalized = NormalizedPermission.from_permission_set(perm_set)

        # Then
        assert normalized.sub_theme_id == ""
        assert normalized.sub_theme_name == ""
        assert normalized.topic_id == ""
        assert normalized.topic_name == ""

    @pytest.mark.django_db
    def test_to_dict_returns_correct_structure(self):
        """
        Given a NormalizedPermission
        When converting to dict
        Then structure contains id and name for each field
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
        result = normalized.to_dict()

        # Then
        assert "theme" in result
        assert "id" in result["theme"]
        assert "name" in result["theme"]

        assert "sub_theme" in result
        assert "topic" in result
        assert "metric" in result
        assert "geography_type" in result
        assert "geography" in result

        # Verify values
        assert result["theme"]["id"] == "2"
        assert result["theme"]["name"] != ""


class TestSubsumption:
    """Test suite for permission subsumption logic."""

    @pytest.mark.django_db
    def test_wildcard_theme_subsumes_specific_theme_same_geography(self):
        """
        Given two permissions with same geography but different themes
        When one has wildcard theme
        Then it subsumes the specific theme
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="-1",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_wildcard_geography_subsumes_specific_geography_same_theme(self):
        """
        Given two permissions with same theme but different geographies
        When one has wildcard geography
        Then it subsumes the specific geography
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="-1",
            geography="-1",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_different_themes_different_geographies_no_subsumption(self):
        """
        Given two permissions with different themes AND different geographies
        When comparing them
        Then neither subsumes the other
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
            geography_type="2",
            geography="E12000008",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert not normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_sub_theme_wildcard_subsumes_specific_topics(self):
        """
        Given same theme and geography
        When one has wildcard at sub-theme level
        Then it subsumes specific topics/metrics
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_topic_wildcard_subsumes_specific_metrics(self):
        """
        Given same theme/sub_theme and geography
        When one has wildcard at topic level
        Then it subsumes specific metrics
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_metric_wildcard_subsumes_specific_metric(self):
        """
        Given same theme/sub_theme/topic and geography
        When one has wildcard metric
        Then it subsumes specific metric
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_geography_type_wildcard_subsumes_specific_type(self):
        """
        Given same theme path
        When one has wildcard geography_type
        Then it subsumes specific geography_type
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="-1",
            geography="-1",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_geography_wildcard_subsumes_specific_geography(self):
        """
        Given same theme path and geography_type
        When one has wildcard geography
        Then it subsumes specific geography
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="-1",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)

    @pytest.mark.django_db
    def test_global_wildcard_subsumes_everything(self):
        """
        Given wildcard theme AND wildcard geography
        Then it subsumes any specific permission
        """
        # Given
        global_wildcard = PermissionSetFactory.create_wildcard_permission_set()
        specific = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        normalized_wildcard = NormalizedPermission.from_permission_set(global_wildcard)
        normalized_specific = NormalizedPermission.from_permission_set(specific)

        # Then
        assert normalized_wildcard.subsumes(normalized_specific)
        assert not normalized_specific.subsumes(normalized_wildcard)

    @pytest.mark.django_db
    def test_partial_overlap_no_subsumption(self):
        """
        Given permissions with partial overlap
        When one has wildcard theme but specific geography
        And other has specific theme but wildcard geography
        Then neither subsumes the other
        """
        # Given
        perm1 = PermissionSetFactory.create_permission_set(
            theme="-1",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",  # Specific
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="-1",  # Wildcard
            geography="-1",
        )

        normalized1 = NormalizedPermission.from_permission_set(perm1)
        normalized2 = NormalizedPermission.from_permission_set(perm2)

        # Then
        assert not normalized1.subsumes(normalized2)
        assert not normalized2.subsumes(normalized1)


class TestBuildPermissionHierarchy:
    """Test suite for build_permission_hierarchy function."""

    @pytest.mark.django_db
    def test_single_permission_no_deduplication(self):
        """
        Given a single permission set
        When building hierarchy
        Then no deduplication occurs
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        user.permission_sets.add(perm)

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        assert result["summary"]["total_permission_sets"] == 1
        assert result["summary"]["deduplicated_count"] == 1
        assert result["summary"]["removed_count"] == 0
        assert len(result["permission_sets"]) == 1

    @pytest.mark.django_db
    def test_removes_fully_subsumed_permission(self):
        """
        Given permission A that fully subsumes permission B
        When building hierarchy
        Then only permission A is returned
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())

        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="-1",
            geography_type="-1",
            geography="-1",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="-1",
            geography_type="2",
            geography="E12000008",
        )

        user.permission_sets.set([perm1, perm2])

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        assert result["summary"]["total_permission_sets"] == 2
        assert result["summary"]["deduplicated_count"] == 1
        assert result["summary"]["removed_count"] == 1

        hierarchy = result["permission_sets"]
        assert len(hierarchy) == 1
        assert hierarchy[0]["geography_type"]["id"] == "-1"

    @pytest.mark.django_db
    def test_keeps_independent_permissions(self):
        """
        Given two permissions that don't subsume each other
        When building hierarchy
        Then both are kept
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())

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

        user.permission_sets.set([perm1, perm2])

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        assert result["summary"]["deduplicated_count"] == 2
        assert result["summary"]["removed_count"] == 0
        assert len(result["permission_sets"]) == 2

    @pytest.mark.django_db
    def test_complex_multi_level_deduplication(self):
        """
        Given multiple overlapping permissions at different levels
        When building hierarchy
        Then correct deduplication occurs
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())

        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="-1",
            metric="-1",
            geography_type="-1",
            geography="-1",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm3 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        perm4 = PermissionSetFactory.create_permission_set(
            theme="5",
            sub_theme="8",
            topic="12",
            metric="-1",
            geography_type="1",
            geography="W92000004",
        )

        user.permission_sets.set([perm1, perm2, perm3, perm4])

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        assert result["summary"]["total_permission_sets"] == 4
        assert result["summary"]["deduplicated_count"] == 2
        assert result["summary"]["removed_count"] == 2

    @pytest.mark.django_db
    def test_summary_contains_correct_statistics(self):
        """
        Given various permission sets
        When building hierarchy
        Then summary contains accurate statistics
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())

        global_perm = PermissionSetFactory.create_wildcard_permission_set()
        specific_perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        user.permission_sets.set([global_perm, specific_perm])

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        summary = result["summary"]
        assert "total_permission_sets" in summary
        assert "deduplicated_count" in summary
        assert "removed_count" in summary
        assert "has_global_access" in summary
        assert "wildcard_themes" in summary

        assert summary["has_global_access"] is True
        assert "* (All)" in summary["wildcard_themes"]

    @pytest.mark.django_db
    def test_hierarchy_structure_is_correct(self):
        """
        Given permission sets
        When building hierarchy
        Then each permission has correct structure
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        user.permission_sets.add(perm)

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        hierarchy = result["permission_sets"]
        assert len(hierarchy) == 1

        permission = hierarchy[0]
        required_fields = [
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography_type",
            "geography",
        ]

        for field in required_fields:
            assert field in permission
            assert "id" in permission[field]
            assert "name" in permission[field]


class TestGetDeduplicatedPermissions:
    """Test suite for get_deduplicated_permissions helper function."""

    @pytest.mark.django_db
    def test_returns_normalized_permission_list(self):
        """
        Given permission sets
        When getting deduplicated permissions
        Then returns list of NormalizedPermission objects
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())
        perm = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        user.permission_sets.add(perm)

        # When
        result = get_deduplicated_permissions(user.permission_sets.all())

        # Then
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], NormalizedPermission)

    @pytest.mark.django_db
    def test_deduplicates_permissions(self):
        """
        Given overlapping permission sets
        When getting deduplicated permissions
        Then subsumed permissions are removed
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())

        perm1 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )

        user.permission_sets.set([perm1, perm2])

        # When
        result = get_deduplicated_permissions(user.permission_sets.all())

        # Then
        assert len(result) == 1
        assert result[0].sub_theme_id == "-1"

    @pytest.mark.django_db
    def test_empty_queryset_returns_empty_hierarchy(self):
        """
        Given an empty queryset
        When building hierarchy
        Then returns empty hierarchy with zero counts
        """
        # Given
        from auth_content.models.users import User
        from auth_content.models.permission_sets import PermissionSet

        user = User.objects.create(user_id=uuid4())

        # When
        result = build_permission_hierarchy(PermissionSet.objects.none())

        # Then
        assert result["summary"]["total_permission_sets"] == 0
        assert result["summary"]["deduplicated_count"] == 0
        assert result["summary"]["removed_count"] == 0
        assert len(result["permission_sets"]) == 0

    @pytest.mark.django_db
    def test_handles_null_fields_gracefully(self):
        """
        Given permission sets with null/empty fields
        When building hierarchy
        Then handles gracefully without errors
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())
        perm = PermissionSetFactory.create(
            theme="2",
            sub_theme="",
            topic="",
            metric="10",
            geography_type="1",
            geography="E92000001",
        )
        user.permission_sets.add(perm)

        # When
        result = build_permission_hierarchy(user.permission_sets.all())

        # Then
        assert result["summary"]["deduplicated_count"] == 1
        hierarchy = result["permission_sets"]
        assert hierarchy[0]["sub_theme"]["id"] is None
        assert hierarchy[0]["topic"]["id"] is None

    @pytest.mark.django_db
    def test_all_wildcards_at_different_levels(self):
        """
        Given permissions with wildcards at various levels
        When building hierarchy
        Then correctly handles all wildcard combinations
        """
        # Given
        from auth_content.models.users import User

        user = User.objects.create(user_id=uuid4())
        perm1 = PermissionSetFactory.create_permission_set(
            theme="-1",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm2 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm3 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="-1",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )
        perm4 = PermissionSetFactory.create_permission_set(
            theme="2",
            sub_theme="2",
            topic="3",
            metric="-1",
            geography_type="1",
            geography="E92000001",
        )

        user.permission_sets.set([perm1, perm2, perm3, perm4])

        result = build_permission_hierarchy(user.permission_sets.all())

        assert result["summary"]["deduplicated_count"] == 1
        hierarchy = result["permission_sets"]
        assert hierarchy[0]["theme"]["id"] == "-1"


class TestGetChoiceLabel:
    """Test suite for _get_choice_label static method."""

    def test_returns_value_for_unknown_field_name(self):
        """
        Given an unknown field name not in the mapping
        When getting choice label
        Then returns the value unchanged (defensive fallback)
        """

        unknown_field = "unknown_field_type"
        test_value = "12345"

        # When
        result = _get_choice_label(unknown_field, test_value)

        # Then
        assert result == test_value

    def test_returns_value_for_empty_field_name(self):
        """
        Given an empty field name
        When getting choice label
        Then returns the value unchanged
        """

        # When
        result = _get_choice_label("", "12345")

        # Then
        assert result == "12345"

    def test_returns_value_for_none_field_name(self):
        """
        Given None as field name
        When getting choice label
        Then returns the value unchanged
        """

        # When
        result = _get_choice_label(None, "12345")

        # Then
        assert result == "12345"

    @pytest.mark.django_db
    def test_returns_name_for_valid_theme(self):
        """
        Given a valid field name and value
        When getting choice label
        Then returns the name from database
        """
        fake_theme_name_one = "respiratory"
        fake_theme_name_two = "infectious_disease"
        fake_theme_name_three = "immunisation"

        ThemeFactory(name=fake_theme_name_one)
        ThemeFactory(name=fake_theme_name_two)
        ThemeFactory(name=fake_theme_name_three)

        # When
        result = _get_choice_label("theme", "2")

        # Then
        assert result != "2"
        assert result == "infectious_disease"
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.django_db
    def test_returns_value_when_name_lookup_fails(self):
        """
        Given a valid field name but non-existent ID
        When getting choice label and lookup returns None
        Then returns the original value as fallback
        """

        result = _get_choice_label("theme", "99999")

        assert result == "99999"

    @pytest.mark.django_db
    def test_geography_uses_string_id(self):
        """
        Given geography field name
        When getting choice label
        Then uses string value directly (not converted to int)
        """

        # When
        result = _get_choice_label("geography", "E92000001")

        assert isinstance(result, str)

    @pytest.mark.django_db
    def test_other_fields_use_int_id(self):
        """
        Given non-geography field name
        When getting choice label
        Then converts value to int before lookup
        """

        fake_theme_name_one = "respiratory"
        fake_theme_name_two = "infectious_disease"
        fake_theme_name_three = "immunisation"

        ThemeFactory(name=fake_theme_name_one)
        ThemeFactory(name=fake_theme_name_two)
        ThemeFactory(name=fake_theme_name_three)

        # When
        result = _get_choice_label("theme", "3")

        # Then
        assert isinstance(result, str)
        assert result != "3"
