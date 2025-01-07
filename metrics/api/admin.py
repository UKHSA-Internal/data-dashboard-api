from datetime import datetime, timedelta
from django.urls import path
from django.contrib import admin

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.rbac_models import RBACGroupPermission, RBACPermission

admin.site.register(APITimeSeries)
admin.site.register(RBACPermission)
admin.site.register(RBACGroupPermission)


class DashBoardAdmin(admin.AdminSite):
    site_header = "Data Dashboard Admin"
    site_title = "Data Dashboard Admin"
    index_title = "Welcome to Data Dashboard Admin"


dashboard_admin_site = DashBoardAdmin(name="dashboard_admin")
dashboard_admin_site.register(APITimeSeries, APITimeseriesAdmin)
dashboard_admin_site.register(CoreTimeSeries, CoreTimeseriesAdmin)
dashboard_admin_site.register(CoreHeadline, CoreHeadlineAdmin)
