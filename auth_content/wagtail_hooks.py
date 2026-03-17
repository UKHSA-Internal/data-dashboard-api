import json

from wagtail import hooks
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.viewsets.model import ModelViewSetGroup
from django.templatetags.static import static

from auth_content.models import PermissionSet, get_theme_child_map, get_sub_theme_child_map
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class PermissionSetViewSet(SnippetViewSet):
    model = PermissionSet
    menu_label = "Permission Sets"
    icon = "key"


class AuthGroup(ModelViewSetGroup):
    items = (PermissionSetViewSet,)
    menu_label = "Auth"
    menu_icon = "lock"
    menu_order = 300


@hooks.register("register_admin_viewset")
def register_auth_viewset():
    return AuthGroup()

# exposes the mapping of parent to child themes


@hooks.register("insert_editor_js")
def permission_set_theme_mapping():
    mapping = json.dumps(get_theme_child_map())
    return format_html(
        "<script>window.PERMISSIONSET_THEME_MAP = {};</script>", mark_safe(
            mapping)
    )

# exposes the mapping of parent to child themes


@hooks.register("insert_editor_js")
def permission_set_sub_theme_mapping():
    sub_theme_mapping = json.dumps(get_sub_theme_child_map())
    print(sub_theme_mapping)
    return format_html(
        "<script>window.PERMISSIONSET_SUB_THEME_MAP = {};</script>", mark_safe(
            sub_theme_mapping)
    )


@hooks.register("insert_editor_js")
def permission_set_js():
    return format_html('<script src="{}"></script>', static("js/child_theme.js"))
