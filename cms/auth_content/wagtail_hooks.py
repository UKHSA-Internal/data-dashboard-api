from wagtail import hooks
from wagtail.admin.viewsets.model import (
    ModelPermissionPolicy,
    ModelViewSet,
    ModelViewSetGroup,
)

from cms.auth_content.models.api_application import APIApplication
from cms.auth_content.models.permission_sets import PermissionSet
from cms.auth_content.models.users import User


class NoEditPermissionPolicy(ModelPermissionPolicy):
    def user_has_permission(self, user, action):
        if action == "change":
            return False
        return super().user_has_permission(user, action)

    def user_has_permission_for_instance(self, user, action, instance):
        if action == "change":
            return False
        return super().user_has_permission_for_instance(user, action, instance)


class PermissionSetViewSet(ModelViewSet):
    model = PermissionSet
    menu_label = "Permission Sets"
    icon = "key"
    permission_policy = NoEditPermissionPolicy(PermissionSet)
    inspect_view_enabled = True
    inspect_view_fields = ["permission_set_details"]


class UserViewSet(ModelViewSet):
    model = User
    menu_label = "Users"
    icon = "user"


class APIApplicationViewSet(ModelViewSet):
    model = APIApplication
    menu_label = "API Applications"
    icon = "desktop"


class AuthGroup(ModelViewSetGroup):
    items = (PermissionSetViewSet, UserViewSet, APIApplicationViewSet)
    menu_label = "Auth"
    menu_icon = "lock"
    menu_order = 300


@hooks.register("register_admin_viewset")
def register_auth_viewset():
    return AuthGroup()
