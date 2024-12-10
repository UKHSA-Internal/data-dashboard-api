from http import HTTPStatus

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from feedback.api.serializers.questions import (
    SuggestionsSerializer,
)
from feedback.email_server import send_email_v2

SUGGESTIONS_API_TAG = "suggestions"


class SuggestionsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(tags=[SUGGESTIONS_API_TAG], request=SuggestionsSerializer)
    def post(cls, request: Request, *args, **kwargs) -> HttpResponse:
        """This endpoint sends a feedback email to the designated UKHSA recipient account.

        Note that the only environments which will have this functionality are:

        - `test`

        - `prod`

        **Hitting this endpoint in all other environments will not send any emails**

        """
        serializer = SuggestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_email_v2(suggestions=serializer.validated_data)
        return HttpResponse(HTTPStatus.OK.value)
