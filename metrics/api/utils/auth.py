from functools import wraps
from django.http import JsonResponse
import jwt

# TODO  PUBLIC_KEY = os.environ.get("PUBLIC_KEY")
PUBLIC_KEY = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwhvqCC+37A+UXgcvDl+7\nnbVjDI3QErdZBkI1VypVBMkKKWHMNLMdHk0bIKL+1aDYTRRsCKBy9ZmSSX1pwQlO\n/3+gRs/MWG27gdRNtf57uLk1+lQI6hBDozuyBR0YayQDIx6VsmpBn3Y8LS13p4pT\nBvirlsdX+jXrbOEaQphn0OdQo0WDoOwwsPCNCKoIMbUOtUCowvjesFXlWkwG1zeM\nzlD1aDDS478PDZdckPjT96ICzqe4O1Ok6fRGnor2UTmuPy0f1tI0F7Ol5DHAD6pZ\nbkhB70aTBuWDGLDR0iLenzyQecmD4aU19r1XC9AHsVbQzxHrP8FveZGlV/nJOBJw\nFwIDAQAB\n-----END PUBLIC KEY-----\n"


def authorised_route(func):
    @wraps(func)
    def wrap(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization")
            token = token.split("Bearer ")[1]
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
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
