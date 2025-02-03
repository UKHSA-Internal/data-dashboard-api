from django.contrib import admin

from metrics.data.models.api_models import APITimeSeries
from metrics.api.models import (
    ApiGroup,
    ApiPermission,
)

admin.site.register(APITimeSeries)
admin.site.register(ApiGroup)
admin.site.register(ApiPermission)
