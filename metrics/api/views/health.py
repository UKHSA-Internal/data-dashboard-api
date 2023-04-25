from http import HTTPStatus

from django.http import HttpResponse
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        return HttpResponse(HTTPStatus.OK.value)
