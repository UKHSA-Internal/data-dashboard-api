from http import HTTPStatus

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView

import config
from metrics.interfaces.health.probes import HealthProbeManagement


class HealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        """This health probe can be used to determine whether the service is ready.

        Notes:
            This is a shallow probe, it does not check any upstream services.
            The response body reports the build metadata
            which was baked into the image at build time.

        Returns:
            An `HTTP 200 OK` response with a JSON body containing
            `status`, `version` and `commit_sha`

        """
        return JsonResponse(
            data={
                "status": "OK",
                "version": config.APP_VERSION,
                "commit_sha": config.COMMIT_SHA,
            },
            status=HTTPStatus.OK.value,
        )


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
