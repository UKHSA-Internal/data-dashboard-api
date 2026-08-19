from functools import reduce
from operator import and_, or_

from django.db.models import Q
from wagtail.query import PageQuerySet

from cms.auth_content.models.non_public_page import get_non_public_page_types
from common.auth.permissions import WILDCARD_ID_VALUE, PermissionRowType


def filter_public_pages(*, queryset: PageQuerySet) -> PageQuerySet:
    """
    Adds filters to the queryset to ensure only public pages are returned when the queryset is run.

    If the queryset model is set to a specific non-public page type then this function simply adds a filter on the
    is_public flag and returns the modified queryset.

    Otherwise, the queryset model should be the base Page type so we add a filter for each non-public page type to
    ensure no non-public pages of those types are returned. Due to the way Wagtail's default pages endpoint works (which
    we use) we can't do this using a join we have to do it using an in query on the page ID and subqueries.

    Args:
        queryset: the queryset to add filters to

    Returns: the altered queryset
    """
    non_public_pages = get_non_public_page_types()

    if queryset.model in non_public_pages:
        # if we have a specific page model, and it is one of our non-public page types then we can just directly add an
        # is_public filter to the queryset
        queryset = queryset.filter(is_public=True)
    else:
        # otherwise, add exclusions on each of our non-public page classes to ensure only public pages are returned for
        # the type
        for subclass in non_public_pages:
            queryset = queryset.exclude(
                pk__in=subclass.objects.filter(is_public=False).values_list(
                    "pk", flat=True
                )
            )

    return queryset


def filter_non_public_pages(
    *,
    queryset: PageQuerySet,
    permission_sets: list[PermissionRowType],
) -> PageQuerySet:
    """
    Adds filters to the queryset to ensure only pages that can be viewed by the given permission sets are returned when
    the queryset is run. This includes public pages as well as those explicitly allowed by the permission sets.

    Args:
        queryset: the queryset to add filters to
        permission_sets: the permission sets to filter on

    Returns: the altered queryset
    """
    perm_predicate = reduce(or_, map(_to_predicate, permission_sets), Q())
    non_public_filter = Q(is_public=False) & ~perm_predicate

    non_public_pages = get_non_public_page_types()
    if queryset.model in non_public_pages:
        # if the queryset model is a non-public page type then query it directly
        queryset = queryset.exclude(non_public_filter)
    else:
        # otherwise, loop through the non-public page types and add a filter for each using a subquery
        for subclass in non_public_pages:
            queryset = queryset.exclude(
                pk__in=(subclass.objects.filter(non_public_filter)).values_list(
                    "pk", flat=True
                )
            )

    return queryset


def _to_predicate(permission_set: PermissionRowType) -> Q:
    """
    Given a single permission set, returns the conditions necessary to filter a non-public page based on it.

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
            # create a predicate which matches the field to an ID value exactly (e.g. page_theme=1)
            Q(**{f"page_{field}": permission_set[field]["id"]})
            if permission_set[field]["id"] != WILDCARD_ID_VALUE
            # if this is a wildcard, create a predicate that will always succeed (e.g. page_theme is not null)
            else Q(**{f"page_{field}__isnull": False})
        )
        for field in ("theme", "sub_theme", "topic")
        # skip missing fields
        if field in permission_set
    ]

    # create a single Q object which combines all the predicates using an and
    return reduce(and_, predicates, Q())
