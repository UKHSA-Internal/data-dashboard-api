from django.urls import path
from django.contrib import admin

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.rbac_models import RBACGroupPermission, RBACPermission

admin.site.register(APITimeSeries)
admin.site.register(RBACPermission)
admin.site.register(RBACGroupPermission)

class NoAddPermissionAdmin(admin.AdminSite):

    def get_urls(self):
        super().get_urls()

    def has_add_permission(self, request):
        return False


# admin.site = NoAddPermissionAdmin(name="readonly_admin")
