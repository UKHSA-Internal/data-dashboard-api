import logging
from typing import List
from functools import wraps

from django.http import JsonResponse
from rest_framework.serializers import Serializer
import jwt

from metrics.api.models import (
    ApiGroup,
    ApiPermission,
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
            print("her-------> 1")
            group = ApiGroup.objects.get(name=group_id)
            request.group_permissions = list(group.permissions.all())
            print("group_permissions ------> ", request.group_permissions)
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
            group_permissions: List[ApiPermission] = getattr(request, "group_permissions", [])

            original_to_representation = self.to_representation

            def new_to_representation(instance):
                data = original_to_representation(instance)
                # if the group permissions contains a key equal to the current data dict key's value
                # then check the group permissions
                data_types = ["theme", "sub_theme", "topic", "geography_type", "geography", "age", "stratum"]

                print("group_permission -----> ", group_permissions[0])
                ## 1.

                # for restricted_field in restricted_fields:
                #     field_match = False
                #     for group_permission in group_permissions:

                        # TODO Monday, add infctions diseases rows in database

                        # 1. check that theme is not None
                        # 2. go and get the theme object and then only show response JSON for that theme type.
                        # 3. check that subtheme is not None
                        # 4. go and check that

                        # for data_type in data_types:
                        #     matched_data_type = False
                        #     group_permission_attr = getattr(group_permission, data_type, None)
                        #     if group_permission_attr:
                        #         # 5. remove all objects that don't match this data type's name
                        #         group_permission_attr_name = getattr(group_permission_attr, "name", None)
                        #         for data_key in data.keys():
                        #             if data_key == data_type: # e.g theme == theme"
                        #                 if data[data_key] == group_permission_attr_name:
                        #                     matched_data_type = True
                        #         if not matched_data_type:
                        #             return None
                return data

            self.to_representation = new_to_representation

        serializer_class.__init__ = init
        return serializer_class

    return decorator
