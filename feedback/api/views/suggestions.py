import logging
from http import HTTPStatus

from botocore.exceptions import ParamValidationError
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from feedback.api.serializers.questions import (
    SuggestionsSerializer,
)
from feedback.email_server import send_email

SUGGESTIONS_API_TAG = "suggestions"
logger = logging.getLogger(__name__)


class SuggestionsV2View(APIView):
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
        logger.info("Email request received")

        serializer = SuggestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            logger.info("sending mail from view")
            send_email(suggestions=serializer.validated_data)
        except ParamValidationError:
            logger.info("ParamValidationError", exc_info=True)
            return Response(status=HTTPStatus.BAD_REQUEST)
        return HttpResponse(HTTPStatus.OK.value)
