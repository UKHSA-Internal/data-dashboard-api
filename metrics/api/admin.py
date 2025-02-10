from django.contrib import admin

from metrics.api.models import (
    ApiGroup,
    ApiPermission,
)
from metrics.data.models.api_models import APITimeSeries

admin.site.register(APITimeSeries)
admin.site.register(ApiGroup)
admin.site.register(ApiPermission)
