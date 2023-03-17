from django.contrib import admin

from metrics.data.models.core_models import TimeSeries

admin.site.register(TimeSeries)
