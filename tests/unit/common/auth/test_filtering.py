from unittest.mock import MagicMock, patch

from django.db.models import Q

from common.auth.filtering import (
    _to_predicate,
    filter_for_permissions,
    filter_non_public_data,
)
from common.auth.permissions import WILDCARD_ID_VALUE


class TestFilterForPermissions:

    def test_filters_directly_when_no_permission_sets(self):
        """
        Given a mock queryset with no permission_sets
        When the queryset is filtered
        Then the queryset is filtered directly with is_public=True
        """
        # given
        queryset_out = MagicMock()
        queryset_in = MagicMock(filter=MagicMock(return_value=queryset_out))
        permission_sets = None

        # when
        result = filter_for_permissions(
            queryset=queryset_in, permission_sets=permission_sets
        )

        # then
        assert result == queryset_out
        queryset_in.filter.assert_called_once_with(is_public=True)

    def test_filters_non_public_data_with_global_permissions(self):
        """
        Given a mock queryset with permission_sets that have global access
        When the queryset is filtered
        Then the queryset is not filtered
        """
        # given
        queryset_in = MagicMock()
        permission_sets = {"summary": {"has_global_access": True}}

        # when
        result = filter_for_permissions(
            queryset=queryset_in, permission_sets=permission_sets
        )

        # then
        assert result == queryset_in
        queryset_in.filter.assert_not_called()

    @patch("common.auth.filtering.filter_non_public_data")
    def test_filters_non_public_data_with_permission_sets(
        self, mock_filter_non_public_data
    ):
        """
        Given a mock queryset with permission_sets
        When the queryset is filtered
        Then the queryset is filtered with filter_non_public_data
        """
        # given
        queryset_out = MagicMock()
        mock_filter_non_public_data.return_value = queryset_out
        queryset_in = MagicMock()
        permission_sets = {
            "summary": {"has_global_access": False},
            "permission_sets": {},
        }

        # when
        result = filter_for_permissions(
            queryset=queryset_in, permission_sets=permission_sets
        )

        # then
        assert result == queryset_out
        mock_filter_non_public_data.assert_called()


class TestFilterNonPublicData:

    @patch("common.auth.filtering._to_predicate")
    def test_filters_queryset_for_non_public(self, mock_to_filter):
        """
        Given a mock queryset which is configured to use a fake non-public page model
        When the non-public page queryset is filtered with fake permission sets
        Then the queryset is filtered directly with the combined non-public filter
        """
        # given
        queryset_out = MagicMock()
        queryset_in = MagicMock(exclude=MagicMock(return_value=queryset_out))

        permission_set_1 = MagicMock()
        permission_set_2 = MagicMock()
        permission_sets = [permission_set_1, permission_set_2]

        predicate_1 = Q(theme="10")
        predicate_2 = Q(topic="20")
        mock_to_filter.side_effect = [predicate_1, predicate_2]

        perm_filters = predicate_1 | predicate_2
        expected_filter = Q(is_public=False) & ~perm_filters

        # when
        result = filter_non_public_data(
            queryset=queryset_in, permission_sets=permission_sets
        )

        # then
        assert result == queryset_out
        mock_to_filter.assert_any_call(permission_set_1)
        mock_to_filter.assert_any_call(permission_set_2)
        assert mock_to_filter.call_count == 2
        queryset_in.exclude.assert_called_once_with(expected_filter)


class TestToPredicate:
    def test_builds_filter_for_specific_fields(self):
        """
        Given a permission set with only 3 specific fields
        When the permission set is transformed to a query predicate
        Then a conjunction is returned for those three access fields
        """
        # given
        permission_set = {
            "theme": {"name": "theme-1", "id": 1},
            "sub_theme": {"name": "sub-theme-2", "id": 2},
            "topic": {"name": "topic-3", "id": 3},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        expected = Q(theme="theme-1") & Q(sub_theme="sub-theme-2") & Q(topic="topic-3")
        assert result == expected

    def test_omits_fields_with_wildcard_ids(self):
        """
        Given a permission set with wildcard IDs for some access fields
        When the permission set is transformed to a query predicate
        Then wildcard fields are omitted from the predicate
        """
        # given
        permission_set = {
            "theme": {"id": WILDCARD_ID_VALUE},
            "sub_theme": {"name": "sub-theme-2", "id": 2},
            "topic": {"id": WILDCARD_ID_VALUE},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        assert result == (
            Q(theme__isnull=False) & Q(sub_theme="sub-theme-2") & Q(topic__isnull=False)
        )

    def test_returns_empty_filter_when_all_ids_are_wildcards(self):
        """
        Given a permission set with wildcard IDs for all access fields
        When the permission set is transformed to a query predicate
        Then an empty predicate is returned
        """
        # given
        permission_set = {
            "theme": {"id": WILDCARD_ID_VALUE},
            "sub_theme": {"id": WILDCARD_ID_VALUE},
            "topic": {"id": WILDCARD_ID_VALUE},
            "metric": {"id": WILDCARD_ID_VALUE},
            "geography_type": {"id": WILDCARD_ID_VALUE},
            "geography": {"id": WILDCARD_ID_VALUE},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        assert result == (
            Q(theme__isnull=False)
            & Q(sub_theme__isnull=False)
            & Q(topic__isnull=False)
            & Q(metric__isnull=False)
            & Q(geography_type__isnull=False)
            & Q(geography__isnull=False)
        )

    def test_includes_all_fields_when_building_predicate(self):
        """
        Given a permission set that includes geography and metric fields
        When it is transformed to a filter predicate
        Then all fields influence the result
        """
        # given
        permission_set = {
            "theme": {"name": "theme-1", "id": 1},
            "sub_theme": {"id": WILDCARD_ID_VALUE},
            "topic": {"id": WILDCARD_ID_VALUE},
            "metric": {"name": "metric-1", "id": 1},
            "geography_type": {"name": "geo-type-3", "id": 3},
            "geography": {"name": "geo-abc", "id": 1},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        assert result == (
            Q(theme="theme-1")
            & Q(sub_theme__isnull=False)
            & Q(topic__isnull=False)
            & Q(metric="metric-1")
            & Q(geography_type="geo-type-3")
            & Q(geography="geo-abc")
        )
