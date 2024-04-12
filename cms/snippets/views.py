from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from cms.snippets.serializers import (
    GlobalBannerResponseSerializer,
    GlobalBannerSerializer,
)


class GlobalBannerView(APIView):
    permission_classes = []

    @extend_schema(
        tags=["cms"], responses={HTTPStatus.OK: GlobalBannerResponseSerializer}
    )
    def get(self, request, *args, **kwargs) -> Response:
        """
        This endpoint returns data associated with the currently active global banner

        Note that if there is no active banner then the response will look like:

        ```
        {"active_global_banner": null}
        ```

        """
        serializer = GlobalBannerSerializer()
        serialized_response_data: dict[str, ReturnDict[str, str] | None] = (
            serializer.data
        )

        return Response(data=serialized_response_data, status=HTTPStatus.OK)
