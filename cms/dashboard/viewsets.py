import logging
from itertools import chain

from django.db.models import Exists, OuterRef, Q
from django.urls import path
from django.urls.resolvers import RoutePattern
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet

from caching.private_api.decorators import cache_response
from cms.auth_content.auth_utils import is_auth_enabled
from cms.auth_content.constants import WILDCARD_ID_VALUE
from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.metrics_documentation.models.child import MetricsDocumentationChildEntry
from cms.topic.models import TopicPage
from metrics.api.settings import auth

logger = logging.getLogger(__name__)
AUTH_ENABLED = is_auth_enabled()


def check_permissions(user_permissions, theme_id, sub_theme_id, topic_id) -> bool:
    if not isinstance(user_permissions, list):
        return False

    for permission in user_permissions:
        permission_theme_id = permission.get("theme", {}).get("id")
        permission_sub_theme_id = permission.get("sub_theme", {}).get("id")
        permission_topic_id = permission.get("topic", {}).get("id")

        if permission_theme_id == WILDCARD_ID_VALUE:
            return True

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == WILDCARD_ID_VALUE
        ):
            return True

        if (
            permission_theme_id == theme_id
            and permission_sub_theme_id == sub_theme_id
            and (permission_topic_id in {WILDCARD_ID_VALUE, topic_id})
        ):
            return True

    return False


@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(PagesAPIViewSet):
    # This is the /pages (or proxy/pages env dependent endpoint)
    permission_classes = []
    base_serializer_class = ListablePageSerializer
    listing_default_fields = PagesAPIViewSet.listing_default_fields + ["show_in_menus"]
    detail_only_fields = []

    def get_queryset(self):
        """Returns the queryset as per the individual models

        Notes:
            The base class `UKHSAPage` sits between
            Wagtail's `Page` and our page models.
            This includes custom logic for building URLs.
            To give the list endpoint the know-how to build URLs,
            the queryset should be returned as per the individual models.
            Since the models reimplement `get_url_parts()` by virtue
            of the base abstract class `UKHSAPage`

            The use of `specific()` here is horribly inefficient.
            But we already cache this endpoint in Redis,
            so we only pay the penalty once per cache flush.

        Returns:
            Queryset of each page model.
            E.g.
                `<PageQuerySet [<LandingPage: UKHSA data dashboard>, <TopicPage: COVID-19>, ...]>`

        """
        queryset = super().get_queryset()

        if AUTH_ENABLED:

            req = self.request

            if req.auth is None:
                filtered_queryset = queryset.annotate(
                    is_public_topic_page=Exists(
                        TopicPage.objects.filter(
                            page_ptr_id=OuterRef("pk"),
                            is_public=True,
                        )
                    ),
                    is_public_metrics_doc_child_page=Exists(
                        MetricsDocumentationChildEntry.objects.filter(
                            page_ptr_id=OuterRef("pk"),
                            is_public=True,
                        )
                    ),
                ).filter(
                    Q(is_public_topic_page=True)
                    | Q(is_public_metrics_doc_child_page=True)
                    | ~Q(
                        content_type__model__in=[
                            "topicpage",
                            "metricsdocumentationchildentry",
                        ]
                    )
                )

            else:
                logger.info(
                    "User %s has total permission sets: %s",
                    req.user.username,
                    req.user.permission_sets["summary"]["total_permission_sets"],
                )
                has_global_access = req.user.permission_sets["summary"][
                    "has_global_access"
                ]

                if has_global_access:
                    logger.info("User %s has global access", req.user.username)
                    filtered_queryset = queryset

                else:
                    user_permissions = req.user.permission_sets["permission_sets"]
                    pages_to_check = chain(
                        (
                            (page.id, page.topicpage)
                            for page in queryset.type(TopicPage)
                        ),
                        (
                            (page.id, page.metricsdocumentationchildentry)
                            for page in queryset.type(MetricsDocumentationChildEntry)
                        ),
                    )
                    allowed_page_ids = [
                        page_id
                        for page_id, page in pages_to_check
                        if page.is_public
                        or check_permissions(
                            user_permissions,
                            page.theme,
                            page.sub_theme,
                            page.topic,
                        )
                    ]

                    public_pages = queryset.not_type(
                        TopicPage, MetricsDocumentationChildEntry
                    )
                    permitted_private_pages = queryset.filter(id__in=allowed_page_ids)

                    filtered_queryset = public_pages | permitted_private_pages

            return filtered_queryset.specific()
        return queryset.specific()

    @cache_response()
    def listing_view(self, request: Request) -> Response:
        """This endpoint returns a list of published pages from the CMS (Wagtail).
        The payload includes page `title`, `id` and `meta` data about each page.
        """
        return super().listing_view(request=request)

    @cache_response()
    def detail_view(self, request: Request, pk: int) -> Response:
        """This end point returns a page from the CMS based on a Page `ID`."""
        return super().detail_view(request=request, pk=pk)


@extend_schema(tags=["cms"])
class CMSDraftPagesViewSet(PagesAPIViewSet):
    base_serializer_class = CMSDraftPagesSerializer
    permission_classes = []

    def detail_view(self, request: Request, pk: int) -> Response:
        """This endpoint returns a page including any unpublished changes in its payload.

        **Note:** this only returns `published` pages with `unpublished` changes.
        """
        instance = self.get_object()
        instance = instance.get_latest_revision_as_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @classmethod
    def get_urlpatterns(cls) -> list[RoutePattern]:
        """This returns a list of URL patterns for the viewset.

        Notes:
            Only the detail `/{id}` path is included.

        """
        return [
            path("<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
