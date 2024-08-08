from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from cms.snippets.serializers import (
    MenuResponseSerializer,
    MenuSerializer,
)


class MenuView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(tags=["cms"], responses={HTTPStatus.OK: MenuResponseSerializer})
    @cache_response
    def get(cls, request, *args, **kwargs) -> Response:
        """
        This endpoint returns the state of the currently active `Menu`

        Note that if there is no active banner then the response will look like:

        ```
        {"active_menu": null}
        ```

        """
        serializer = MenuSerializer()
        return Response(data=serializer.data, status=HTTPStatus.OK)
