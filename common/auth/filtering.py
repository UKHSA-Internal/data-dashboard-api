from functools import reduce
from operator import and_, or_

from django.db.models import Q, QuerySet

from common.auth.permissions import (
    WILDCARD_ID_VALUE,
    PermissionRowType,
    PermissionSetsType,
)


def filter_for_permissions(
    *,
    queryset: QuerySet,
    permission_sets: PermissionSetsType | None = None,
) -> QuerySet:
    if permission_sets:
        if not permission_sets["summary"]["has_global_access"]:
            queryset = filter_non_public_data(
                queryset=queryset,
                permission_sets=permission_sets["permission_sets"],
            )
    else:
        queryset = queryset.filter(is_public=True)

    return queryset


def filter_non_public_data(
    *,
    queryset: QuerySet,
    permission_sets: list[PermissionRowType],
) -> QuerySet:
    """
    Adds filters to the queryset to ensure only data that can be viewed by the given permission sets are returned when
    the queryset is run. This includes public data as well as that explicitly allowed by the permission sets.

    Args:
        queryset: the queryset to add filters to
        permission_sets: the permission sets to filter on

    Returns: the altered queryset
    """
    perm_predicate = reduce(or_, map(_to_predicate, permission_sets), Q())
    non_public_filter = Q(is_public=False) & ~perm_predicate

    return queryset.exclude(non_public_filter)


def _to_predicate(permission_set: PermissionRowType) -> Q:
    """
    Given a single permission set, returns the conditions necessary to filter data based on it.

    This function doesn't do any shortcutting to avoid assuming the hierarchical structure of the permission set itself.
    This makes it future-proof:
    - if the permission set is hierarchical and a wildcard in the theme means a wildcard will be present in the
      sub-theme and topic then we produce the correct predicate
    - if the permission set isn't hierarchical and any field can be a wildcard or a value, then we produce the correct
      predicate
    The only downside to this is a performance hit of potentially asking the db to do more work than it needs to but if
    that becomes an issue we can look at optimisations then.

    Args:
        permission_set: the permission set to create the filter for

    Returns:
        a Q object
    """
    # create a predicate for each of the fields we care about
    predicates = [
        (
            # create a predicate which matches the field to a value exactly (e.g. theme="infectious_disease")
            Q(**{field: value["name"]})
            if value["id"] != WILDCARD_ID_VALUE
            # if this is a wildcard, create a predicate that will always succeed (e.g. theme is not null)
            else Q(**{f"{field}__isnull": False})
        )
        for field, value in permission_set.items()
    ]

    # create a single Q object which combines all the predicates using an and
    return reduce(and_, predicates, Q())
