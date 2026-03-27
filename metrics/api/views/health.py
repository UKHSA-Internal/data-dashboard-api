from http import HTTPStatus

from django.http import HttpResponse
from rest_framework.views import APIView

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


class HealthView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """Health probe + optional metrics"""

        # 👇 your hidden metrics endpoint
        if request.GET.get("metrics") == "1":
            return HttpResponse(
                generate_latest(),
                content_type=CONTENT_TYPE_LATEST,
                status=HTTPStatus.OK.value,
            )

        return HttpResponse(status=HTTPStatus.OK.value)

class InternalHealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        """This health probe can be used to determine whether the service is ready.

        If any upstream services are not available then an `HTTP 503 SERVICE UNAVAILABLE` response will be returned.

        Otherwise, an `HTTP 200 OK` response will be returned.

        """
        health_probe_management = HealthProbeManagement()
        is_healthy: bool = health_probe_management.perform_health_check()

        if is_healthy:
            return HttpResponse(status=HTTPStatus.OK.value)

        return HttpResponse(status=HTTPStatus.SERVICE_UNAVAILABLE.value)
