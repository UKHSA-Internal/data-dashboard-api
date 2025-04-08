from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request
from rest_framework.response import Response


class NoIndexNoFollowMiddleware(MiddlewareMixin):
    @classmethod
    def process_response(cls, request: Request, response: Response) -> Response:
        response["X-Robots-Tag"] = "noindex, nofollow"
        return response
