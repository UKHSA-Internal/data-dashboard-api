from django.contrib import admin

from metrics.data.models.api_models import APITimeSeries
from metrics.api.models import (
    DatasetGroup,
    DatasetGroupMapping,
)

admin.site.register(APITimeSeries)
admin.site.register(DatasetGroup)
admin.site.register(DatasetGroupMapping)
