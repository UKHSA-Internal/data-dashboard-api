from datetime import datetime, timedelta
from django.urls import path
from django.contrib import admin

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries, CoreHeadline

from metrics.api.admin_models.api_model_admin import APITimeseriesAdmin
from metrics.api.admin_models.core_model_admin import CoreTimeseriesAdmin, CoreHeadlineAdmin


class DashBoardAdmin(admin.AdminSite):
    site_header = "Data Dashboard Admin"
    site_title = "Data Dashboard Admin"
    index_title = "Welcome to Data Dashboard Admin"


dashboard_admin_site = DashBoardAdmin(name="dashboard_admin")
dashboard_admin_site.register(APITimeSeries, APITimeseriesAdmin)
dashboard_admin_site.register(CoreTimeSeries, CoreTimeseriesAdmin)
dashboard_admin_site.register(CoreHeadline, CoreHeadlineAdmin)
