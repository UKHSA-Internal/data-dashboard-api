class JwtDetectionMiddleware:
    """
    Detects whether a JWT is present in the Authorization header.
    Does NOT decode or validate it — only checks its existence.
    This will be extended as part of the non-public work.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        # Expected format (this might change once JWT fully implemented):
        # "Bearer <token>" and token itself is three parts separated by "."

        has_jwt = False

        if auth_header.startswith("Bearer ") and len(auth_header.split()) == 2:
            token = auth_header.split()[1]
            parts = token.split(".")

            if len(parts) == 3:
                has_jwt = True

        # Store on the request for downstream use
        request.has_jwt = has_jwt

        return self.get_response(request)
