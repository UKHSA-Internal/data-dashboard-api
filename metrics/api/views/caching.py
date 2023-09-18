from http import HTTPStatus

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from caching.handlers import force_cache_refresh_for_all_pages


class CacheView(APIView):
    permission_classes = [HasAPIKey]

    @staticmethod
    @extend_schema(tags=["caching"], deprecated=True)
    def put(*args, **kwargs):
        """**Note that this endpoint is experimental**"""
        force_cache_refresh_for_all_pages()
        return HttpResponse(status=HTTPStatus.OK.value)
