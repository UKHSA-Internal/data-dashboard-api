from django.contrib import admin
from .mixins import ReadOnlyMixin


class CoreTimeseriesAdmin(ReadOnlyMixin, admin.ModelAdmin):
    list_filter = [
        "metric",
        "age",
        "sex",
        "stratum",
        "geography",
        "geography__geography_type",
        "date",
    ]

    autocomplete_fields = [
        "geography",
    ]

    list_display = [
        "metric_frequency",
        "age",
        "month",
        "metric",
        "metric_value",
        "metric__metric_group",
        "geography",
        "geography__geography_code",
        "geography__geography_type",
        "stratum",
        "sex",
        "year",
        "epiweek",
        "refresh_date",
        "date",
        "embargo",
        "in_reporting_delay_period",
    ]


class CoreHeadlineAdmin(ReadOnlyMixin, admin.ModelAdmin):
    list_filter = [
        "metric",
        "age",
        "sex",
        "stratum",
        "geography",
        "geography__geography_type",
    ]

    list_display = [
        "metric",
        "age",
        "sex",
        "stratum",
        "geography",
        "refresh_date",
        "period_start",
        "period_end",
        "embargo",
        "geography__geography_type",
    ]
