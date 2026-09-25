from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from public_api.auth import is_authenticated_request
from public_api.version.v3.serializers.api_request_serializer import (
    APIDTO,
    APIRequestSerializerv3,
)

PUBLIC_API_TAG = "public-api-v3"
PRIVATE_CACHE_CONTROL = "private, no-cache"


def add_private_cache_control_header(
    *, request: Request, response: Response
) -> Response:
    """Prevent shared caching of responses made for authenticated consumers."""
    if is_authenticated_request(request):
        response["Cache-Control"] = PRIVATE_CACHE_CONTROL

    return response


class BaseNestedAPIViewV3(GenericAPIView):
    api_model = None
    url_prefix = None

    @property
    def lookup_field(self):
        raise NotImplementedError

    @property
    def serializer_class(self):
        raise NotImplementedError

    def _build_request_serializer(self, *, request: Request) -> APIRequestSerializerv3:
        serializer_context = {
            "request": request,
            "lookup_field": self.lookup_field,
            "api_model": self.api_model,
            "url_prefix": self.url_prefix,
        }
        return APIRequestSerializerv3(context=serializer_context)

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer: APIRequestSerializerv3 = self._build_request_serializer(
            request=request
        )
        dto_slice: list[APIDTO] = serializer.build_dto_slice()

        serializer = self.get_serializer(dto_slice, many=True)
        response = Response(data=serializer.data)

        return add_private_cache_control_header(request=request, response=response)
