from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from auth_content.models.permission_sets import PermissionSet
from auth_content.models.users import User


class PermissionSetViewSet(ModelViewSet):
    model = PermissionSet
    menu_label = "Permission Sets"
    icon = "key"


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
