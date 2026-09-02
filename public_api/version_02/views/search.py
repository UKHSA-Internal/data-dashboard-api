from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.api.v2.serializers import get_serializer_class
from wagtail.models import Page

from cms.topic.models import TopicPage
from public_api.version_02.views.base import PUBLIC_API_TAG


@extend_schema(tags=[PUBLIC_API_TAG])
class SearchView(APIView):
    """This endpoint provides search results and could in the future provide
    autocomplete suggestions etc.

    """

    def get(self, request: Request):
        search = request.GET.get("search")
        limit = int(request.GET.get("limit", 0))
        fields = request.GET.get("fields", ["title", "slug"])
        meta = request.GET.get("meta", ["id"])
        topic_results = TopicPage.objects.all().search(search)
        if not limit or topic_results.count() < limit:
            # TODO: go get more
            # results = queryset
            results = topic_results
        else:
            results = topic_results[0:limit]
        print(f"AIDAN: returning {results}")
        serialized = get_serializer_class(Page, fields, meta)(results, many=True)
        return Response(serialized.data)
