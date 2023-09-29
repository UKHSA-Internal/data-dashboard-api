from http import HTTPStatus

from django.http import HttpResponse
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        """This health probe can be used to determine whether the service is ready.

        Note that if the service is running as a `PRIVATE_API` then the cache will be checked first.

        In this case if the cache is not completely hydrated then a `503 SERVICE UNAVAILABLE` response will be returned

        Otherwise, a `200 OK` response will be returned

        """
        # CDD-1157: Temporarily disable cache-specific health check for private API
        # if config.APP_MODE == "PRIVATE_API":
        #     try:
        #         check_cache_for_all_pages()
        #     except CacheCheckResultedInMissError:
        #         return HttpResponse(status=HTTPStatus.SERVICE_UNAVAILABLE.value)

        return HttpResponse(status=HTTPStatus.OK.value)
