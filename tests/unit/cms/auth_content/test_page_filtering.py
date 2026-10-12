from unittest.mock import MagicMock, patch

from django.db.models import Q

from cms.auth_content.page_filtering import (
    _to_predicate,
    filter_non_public_pages,
    filter_public_pages,
)
from common.auth.permissions import WILDCARD_ID_VALUE


class TestFilterPublicPages:

    @patch("cms.auth_content.page_filtering.get_non_public_page_types")
    def test_filters_directly_when_queryset_model_is_non_public(
        self, mock_get_non_public_page_types
    ):
        """
        Given a mock queryset which is configured to use a fake non-public page model
        When the public page queryset is filtered
        Then the queryset is filtered directly with is_public=True
        """
        # given
        non_pub_page_type = MagicMock()
        mock_get_non_public_page_types.return_value = [non_pub_page_type]
        queryset_out = MagicMock()
        queryset_in = MagicMock(
            model=non_pub_page_type, filter=MagicMock(return_value=queryset_out)
        )

        # when
        result = filter_public_pages(queryset=queryset_in)

        # then
        assert result == queryset_out
        queryset_in.filter.assert_called_once_with(is_public=True)

    @patch("cms.auth_content.page_filtering.get_non_public_page_types")
    def test_filters_with_subqueries_when_queryset_model_is_base_page(
        self, mock_get_non_public_page_types
    ):
        """
        Given a mock queryset which is configured to use a fake public page model
        When the public page queryset is filtered
        Then the queryset is filtered with a subquery per fake non-public page type
        """
        # given
        non_pub_type_a = MagicMock(objects=MagicMock())
        non_pub_type_b = MagicMock(objects=MagicMock())
        mock_get_non_public_page_types.return_value = [non_pub_type_a, non_pub_type_b]

        queryset = MagicMock(model=MagicMock())

        first_filtered_queryset = MagicMock()
        second_filtered_queryset = MagicMock()
        queryset.exclude.return_value = first_filtered_queryset
        first_filtered_queryset.exclude.return_value = second_filtered_queryset

        a_pk_subquery = MagicMock()
        b_pk_subquery = MagicMock()
        non_pub_type_a.objects.filter.return_value.values_list.return_value = (
            a_pk_subquery
        )
        non_pub_type_b.objects.filter.return_value.values_list.return_value = (
            b_pk_subquery
        )

        # when
        result = filter_public_pages(queryset=queryset)

        # then
        assert result == second_filtered_queryset

        non_pub_type_a.objects.filter.assert_called_once_with(is_public=False)
        non_pub_type_a.objects.filter.return_value.values_list.assert_called_once_with(
            "pk", flat=True
        )
        non_pub_type_b.objects.filter.assert_called_once_with(is_public=False)
        non_pub_type_b.objects.filter.return_value.values_list.assert_called_once_with(
            "pk", flat=True
        )

        queryset.exclude.assert_called_once_with(pk__in=a_pk_subquery)
        first_filtered_queryset.exclude.assert_called_once_with(pk__in=b_pk_subquery)


class TestFilterNonPublicPages:

    @patch("cms.auth_content.page_filtering.get_non_public_page_types")
    @patch("cms.auth_content.page_filtering._to_predicate")
    def test_filters_directly_when_queryset_model_is_non_public(
        self, mock_to_filter, mock_get_non_public_page_types
    ):
        """
        Given a mock queryset which is configured to use a fake non-public page model
        When the non-public page queryset is filtered with fake permission sets
        Then the queryset is filtered directly with the combined non-public filter
        """
        # given
        non_public_page_type = MagicMock()
        mock_get_non_public_page_types.return_value = [non_public_page_type]
        queryset_out = MagicMock()
        queryset_in = MagicMock(
            model=non_public_page_type, exclude=MagicMock(return_value=queryset_out)
        )

        permission_set_1 = MagicMock()
        permission_set_2 = MagicMock()
        permission_sets = [permission_set_1, permission_set_2]

        predicate_1 = Q(page_theme="10")
        predicate_2 = Q(page_topic="20")
        mock_to_filter.side_effect = [predicate_1, predicate_2]

        perm_filters = predicate_1 | predicate_2
        expected_filter = Q(is_public=False) & ~perm_filters

        # when
        result = filter_non_public_pages(
            queryset=queryset_in, permission_sets=permission_sets
        )

        # then
        assert result == queryset_out
        mock_to_filter.assert_any_call(permission_set_1)
        mock_to_filter.assert_any_call(permission_set_2)
        assert mock_to_filter.call_count == 2
        queryset_in.exclude.assert_called_once_with(expected_filter)

    @patch("cms.auth_content.page_filtering.get_non_public_page_types")
    @patch("cms.auth_content.page_filtering._to_predicate")
    def test_filters_with_subqueries_when_queryset_model_is_base_page(
        self, mock_to_filter, get_non_public_page_types
    ):
        """
        Given a mock queryset which is configured to use a fake public page model
        When the non-public page queryset is filtered with fake permission sets
        Then the queryset is filtered with a non-public subquery per fake non-public page type
        """
        # given
        non_pub_type_a = MagicMock(objects=MagicMock())
        non_pub_type_b = MagicMock(objects=MagicMock())
        get_non_public_page_types.return_value = [non_pub_type_a, non_pub_type_b]

        queryset = MagicMock(model=MagicMock())
        first_filtered_queryset = MagicMock()
        second_filtered_queryset = MagicMock()
        queryset.exclude.return_value = first_filtered_queryset
        first_filtered_queryset.exclude.return_value = second_filtered_queryset

        permission_set = {"name": "perm"}
        permission_sets = [permission_set]
        predicate = Q(page_sub_theme="30")
        mock_to_filter.return_value = predicate

        expected_filter = Q(is_public=False) & ~predicate

        a_pk_subquery = MagicMock()
        b_pk_subquery = MagicMock()
        non_pub_type_a.objects.filter.return_value.values_list.return_value = (
            a_pk_subquery
        )
        non_pub_type_b.objects.filter.return_value.values_list.return_value = (
            b_pk_subquery
        )

        # when
        result = filter_non_public_pages(
            queryset=queryset, permission_sets=permission_sets
        )

        # then
        assert result == second_filtered_queryset
        mock_to_filter.assert_called_once_with(permission_set)

        non_pub_type_a.objects.filter.assert_called_once_with(expected_filter)
        non_pub_type_a.objects.filter.return_value.values_list.assert_called_once_with(
            "pk", flat=True
        )
        non_pub_type_b.objects.filter.assert_called_once_with(expected_filter)
        non_pub_type_b.objects.filter.return_value.values_list.assert_called_once_with(
            "pk", flat=True
        )

        queryset.exclude.assert_called_once_with(pk__in=a_pk_subquery)
        first_filtered_queryset.exclude.assert_called_once_with(pk__in=b_pk_subquery)


class TestToPredicate:
    def test_builds_and_filter_for_specific_ids(self):
        """
        Given a permission set with specific IDs for all access fields
        When the permission set is transformed to a query predicate
        Then a conjunction is returned for all three-page access fields
        """
        # given
        permission_set = {
            "theme": {"id": "theme-1"},
            "sub_theme": {"id": "sub-theme-2"},
            "topic": {"id": "topic-3"},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        expected = (
            Q(page_theme="theme-1")
            & Q(page_sub_theme="sub-theme-2")
            & Q(page_topic="topic-3")
        )
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
            "sub_theme": {"id": "sub-theme-2"},
            "topic": {"id": WILDCARD_ID_VALUE},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        assert result == (
            Q(page_theme__isnull=False)
            & Q(page_sub_theme="sub-theme-2")
            & Q(page_topic__isnull=False)
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
        }

        # when
        result = _to_predicate(permission_set)

        # then
        assert result == (
            Q(page_theme__isnull=False)
            & Q(page_sub_theme__isnull=False)
            & Q(page_topic__isnull=False)
        )

    def test_ignores_fields_when_building_predicate(self):
        """
        Given a permission set that includes geography and metric fields
        When it is transformed to a page filter predicate
        Then only theme/sub-theme/topic fields influence the result
        """
        # given
        permission_set = {
            "theme": {"id": "theme-1"},
            "sub_theme": {"id": WILDCARD_ID_VALUE},
            "topic": {"id": WILDCARD_ID_VALUE},
            "metric": {"id": "metric-1"},
            "geography_type": {"id": "geo-type-3"},
            "geography": {"id": "geo-abc"},
        }

        # when
        result = _to_predicate(permission_set)

        # then
        assert result == (
            Q(page_theme="theme-1")
            & Q(page_sub_theme__isnull=False)
            & Q(page_topic__isnull=False)
        )
