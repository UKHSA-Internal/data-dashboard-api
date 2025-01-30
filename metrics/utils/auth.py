import logging
from typing import List
from functools import wraps

from django.http import JsonResponse
from rest_framework.serializers import Serializer
import jwt

from metrics.api.models import (
    DatasetGroup,
    DatasetGroupMapping,
)

from config import PRIVATE_API_INSTANCE, API_PUBLIC_KEY

logger = logging.getLogger(__name__)


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
            query = DatasetGroupMapping.objects.filter(group__name=group_id)
            dataset_names = query.values_list('dataset_name', flat=True)
            request.dataset_names = list(dataset_names)
            print("dataset names ------> ", dataset_names)
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


def get_allowed_dataset_types(request) -> List[str]:
    return getattr(request, "dataset_names", [])


def serializer_permissions(restricted_fields: List[str]):
    def decorator(serializer_class):
        _init = serializer_class.__init__

        @wraps(_init)
        def init(self, *args, **kwargs):
            super(serializer_class, self).__init__(*args, **kwargs)
            request = self.context.get("request", None)
            dataset_names: List[str] = getattr(request, "dataset_names", [])
            for field in restricted_fields:
                if field not in dataset_names:
                    self.fields.pop(field, None)
        serializer_class.__init__ = init
        return serializer_class
    return decorator