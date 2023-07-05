from http import HTTPStatus

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from feedback import send_email
from feedback.serializers.questions import SuggestionsSerializer

SUGGESTIONS_API_TAG = "suggestions"


class SuggestionsView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(tags=[SUGGESTIONS_API_TAG], request=SuggestionsSerializer)
    def post(self, request: Request, *args, **kwargs) -> HttpResponse:
        serializer = SuggestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_email(serializer.validated_data)
        return HttpResponse(HTTPStatus.OK.value)
