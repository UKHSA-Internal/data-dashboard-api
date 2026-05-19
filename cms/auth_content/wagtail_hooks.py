from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.viewsets.model import (
    ModelPermissionPolicy,
    ModelViewSet,
    ModelViewSetGroup,
)

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


class AuthGroup(ModelViewSetGroup):
    items = (PermissionSetViewSet, UserViewSet)
    menu_label = "Auth"
    menu_icon = "lock"
    menu_order = 300


@hooks.register("register_admin_viewset")
def register_auth_viewset():
    return AuthGroup()


@hooks.register("insert_editor_js")
def permission_set_js():
    return format_html('<script src="{}"></script>', static("js/permission_set.js"))
