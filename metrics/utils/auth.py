import logging
import os
from typing import List
from functools import wraps

from django.http import JsonResponse
import jwt

from metrics.api.models import (
    ApiGroup,
    ApiPermission,
)
from metrics.utils.auth_action import (
    MatchThemeSubthemeAction,
    MatchTopLevelFieldsAction,
    MatchFieldAction,
    ValidationAction,
    new_match_dict,
)

from config import PRIVATE_API_INSTANCE, API_PUBLIC_KEY

logger = logging.getLogger(__name__)


def authorised_route(func):
    @wraps(func)
    def wrap(self, request, *args, **kwargs):
        if os.environ.get("PRIVATE_API_INSTANCE") != '1': # TODO get from config
            return func(self, request, *args, **kwargs)
        try:
            # TODO group_id will come from X-... header
            token = request.headers.get("Authorization")
            token = token.split("Bearer ")[1]
            payload = jwt.decode(token, API_PUBLIC_KEY, algorithms=["RS256"])
            group_id = payload["group_id"]
            group = ApiGroup.objects.get(name=group_id)
            request.group_permissions = list(group.permissions.all())
            return func(self, request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired!"})
        except jwt.DecodeError:
            return JsonResponse({"error": "Token decode error!"})
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token error!"})
        except Exception as err:
            # Check if exception originates from a DRF Serializer
            if getattr(err, "get_full_details", None):
                return JsonResponse({"error": err.get_full_details()})
            return JsonResponse({"error": "Invalid token error" })

    return wrap


def get_allowed_dataset_types(request) -> List[str]:
    return getattr(request, "dataset_names", [])


def serializer_permissions():
    def decorator(serializer_class):
        _init = serializer_class.__init__

        @wraps(_init)
        def init(self, *args, **kwargs):
            super(serializer_class, self).__init__(*args, **kwargs)
            request = self.context.get("request", None)
            group_permissions: List[ApiPermission] = getattr(request, "group_permissions", [])

            original_to_representation = self.to_representation

            if os.environ.get("PRIVATE_API_INSTANCE") != '1':  # TODO get from config
                def new_to_representation(instance):
                    data = original_to_representation(instance)
                    data.pop("is_private")
                    return data
            else:
                def new_to_representation(instance):
                    data = original_to_representation(instance)
                    # Handle non private data
                    if not data["is_private"]:
                        data.pop("is_private")
                        return data
                    match_dicts = []
                    for i, group_permission in enumerate(group_permissions):
                        match_dict = new_match_dict()
                        if not MatchThemeSubthemeAction().execute(data, group_permission):
                            continue
                        match_dict["theme"] = MatchTopLevelFieldsAction("theme").execute(data, group_permission)
                        if not match_dict["theme"]:  # Optimization
                            continue
                        match_dict["sub_theme"] = MatchTopLevelFieldsAction("sub_theme").execute(data, group_permission)
                        if not match_dict["sub_theme"]:  # Optimization
                            continue
                        match_dict["topic"] = MatchFieldAction("topic").execute(data, group_permission)
                        match_dict["geography_type"] = MatchFieldAction("geography_type").execute(data, group_permission)
                        match_dict["geography"] = MatchFieldAction("geography").execute(data, group_permission)
                        match_dict["metric"] = MatchFieldAction("metric").execute(data, group_permission)
                        match_dict["age"] = MatchFieldAction("age").execute(data, group_permission)
                        match_dict["stratum"] = MatchFieldAction("stratum").execute(data, group_permission)
                        # append results
                        match_dicts.append(match_dict)
                    # \for - validate results
                    validate = ValidationAction()
                    validate.execute(match_dicts)
                    # Clean up is_private key from output data
                    data.pop("is_private")
                    # action results
                    if validate.did_match:
                        return data
                    return None

            self.to_representation = new_to_representation

        serializer_class.__init__ = init
        return serializer_class

    return decorator
