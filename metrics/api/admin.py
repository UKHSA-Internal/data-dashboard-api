from django.urls import path
from django.contrib import admin

# from metrics.data.models.api_models import APITimeSeries
#
# admin.site.register(APITimeSeries)


class NoAddPermissionAdmin(admin.AdminSite):

    def get_urls(self):
        super().get_urls()

    def has_add_permission(self, request):
        return False


# admin.site = NoAddPermissionAdmin(name="readonly_admin")
