from django.contrib import admin

from metrics.api.models.core_models import TimeSeries

admin.site.register(TimeSeries)
