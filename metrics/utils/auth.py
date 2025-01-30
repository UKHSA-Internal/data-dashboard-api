from functools import wraps
from django.http import JsonResponse
import jwt

from config import PRIVATE_API_INSTANCE, API_PUBLIC_KEY


def authorised_route(func):
    @wraps(func)
    def wrap(self, request, *args, **kwargs):
        if not PRIVATE_API_INSTANCE:
            return func(self, request, *args, **kwargs)
        try:
            token = request.headers.get("Authorization")
            token = token.split("Bearer ")[1]
            payload = jwt.decode(token, API_PUBLIC_KEY, algorithms=["RS256"])
            group_id = payload["group_id"]
            request.group_id = group_id
            return func(self, request, *args, **kwargs)
        except jwt.ExpiredSignatureError as err:
            return JsonResponse({"error": "Token expired!"})
        except jwt.DecodeError as err:
            return JsonResponse({"error": "Token decode error!"})
        except jwt.InvalidTokenError as err:
            return JsonResponse({"error": "Invalid token error!"})
        except KeyError as err:
            return JsonResponse({"error": "Invalid payload error!"})
        except Exception as err:
            print(str(err))
            return JsonResponse({"error": "Authorisation error!"})
    return wrap
