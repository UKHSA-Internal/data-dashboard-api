from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from cms.snippets.serializers import (
    GlobalBannerResponseSerializer,
    GlobalBannerSerializer,
)


class GlobalBannerView(APIView):
    permission_classes = []
    
    @classmethod
    @extend_schema(
        tags=["cms"], responses={HTTPStatus.OK: GlobalBannerResponseSerializer}
    )
    @cache_response()
    def get(cls, request, *args, **kwargs) -> Response:
        """
        This endpoint returns data associated with the currently active global banner

        Note that if there is no active banner then the response will look like:

        ```
        {"active_global_banners": []}
        ```

        """
        serializer = GlobalBannerSerializer()
        serialized_response_data: dict[str, ReturnDict[str, str]] = serializer.data

        return Response(data=serialized_response_data, status=HTTPStatus.OK)
