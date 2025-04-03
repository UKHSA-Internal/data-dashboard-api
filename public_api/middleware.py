from django.utils.deprecation import MiddlewareMixin


class NoIndexNoFollowMiddleware(MiddlewareMixin):
    @classmethod
    def process_response(cls, request, response):
        response["X-Robots-Tag"] = "noindex, nofollow"
        return response
