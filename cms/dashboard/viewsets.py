from django.urls import path
from django.urls.resolvers import RoutePattern
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet

from caching.private_api.decorators import cache_response
from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.metrics_documentation.models.child import MetricsDocumentationChildEntry
from cms.topic.models import TopicPage

from django.db.models import Q



def check_permissions(user_permissions, theme_id, sub_theme_id, topic_id) -> bool:
    for permission in user_permissions:
        if permission.theme.id == -1:
            return True
        if permission.theme.id == theme_id and sub_theme_id == -1:
            return True
        if permission.theme.id == theme_id \
            and (permission.sub_theme.id == sub_theme_id) \
            and (permission.topic.id == -1 or permission.topic.id == topic_id):
            return True

    return False

@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(PagesAPIViewSet):
    # This is the /pages (or proxy/pages env dependent endpoint)
    permission_classes = []
    base_serializer_class = ListablePageSerializer
    listing_default_fields = PagesAPIViewSet.listing_default_fields + ["show_in_menus"]
    detail_only_fields = []

    # **
    # TODO: Is this endpoint used for nonpublic data?
    # I would assume so, which means we need to change the caching - use the decorator?
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

        req = self.request
        
        # for page in queryset.type(TopicPage):
        #     if page.topicpage.theme is not None:
        #         print(f"page.title: {page.title}")
        #         print(f"🦊 page.topicpage.theme (id): {page.topicpage.theme}")

        print(f"👤🦊🦊🦊🦊👤 USER: {req.user} 👤🦊🦊🦊🦊👤")
        if req.auth is None:
            # Filter pages to find those with the is public field (and where is_public is true)
            topic_page_ids_with_is_public = TopicPage.objects.filter(is_public=True, page_ptr__in=queryset).values_list("page_ptr_id", flat=True)
            metric_doc_child_page_ids_with_is_public = MetricsDocumentationChildEntry.objects.filter(is_public=True, page_ptr__in=queryset).values_list("page_ptr_id", flat=True)

            # Combine all public pages into one queryset
            topic_public_pages = queryset.filter(id__in=topic_page_ids_with_is_public)
            metric_child_public_pages = queryset.filter(id__in=metric_doc_child_page_ids_with_is_public)
            is_public_pages = topic_public_pages | metric_child_public_pages
            pages_without_is_public = queryset.not_type(TopicPage, MetricsDocumentationChildEntry)
            public_pages = is_public_pages | pages_without_is_public
            
            filtered_queryset = public_pages
        
        else:

            print(f"🦊🦊🦊🦊🦊🦊🦊🦊 Permission Sets: {req.user.permission_sets} 🦊🦊🦊🦊🦊🦊🦊🦊🦊")
            # print(f"🦊 page.topicpage.theme (id): {page.topicpage.theme}")
            user_permissions = req.user.permission_sets['permission_set_hierarchy']

            # Global access check

            allowed_pages = []
            for page in queryset:
                if page.type(TopicPage):
                    if page.topicpage.is_public:
                        allowed_pages.append(page.id)
                    else:
                        # Compare to users permission themes
                        if check_permissions(user_permissions, page.topicpage.theme.id, page.topicpage.sub_theme.id, page.topicpage.theme.topic.id):
                            allowed_pages.append(page.id)

                elif page.type(MetricsDocumentationChildEntry):
                    if page.metricsdocumentationchildentry.is_public:
                        allowed_pages.append(page.id)
                    else:
                        if check_permissions(user_permissions, page.topicpage.theme.id, page.topicpage.sub_theme.id, page.topicpage.theme.topic.id):
                            allowed_pages.append(page.id)                           

                else:
                    allowed_pages.append(page.id)

            filtered_queryset = queryset.filter(id__in=allowed_pages)
                    
        return filtered_queryset.specific()

    @cache_response()
    def listing_view(self, request: Request) -> Response:
        """This endpoint returns a list of published pages from the CMS (Wagtail).
        The payload includes page `title`, `id` and `meta` data about each page.
        """
        print(f"REQUEST.USER 🦄 {request.user}")
        print(f"I AM LISTING VIEW 🦄: {super().listing_view(request=request)}")
        return super().listing_view(request=request)

    @cache_response()
    def detail_view(self, request: Request, pk: int) -> Response:
        """This end point returns a page from the CMS based on a Page `ID`."""
        print(f"REQUEST.USER 🎯 {request.user}")
        print(f"I AM DETAIL VIEW 🎯: {super().detail_view(request=request, pk=pk)}")
        if request.auth is None:
            print()
            # check the is public flag & only return public pages
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
