from django.contrib import admin
from django.core.paginator import Paginator
from .mixins import ReadOnlyMixin
from metrics.data.models.core_models.supporting import Geography, Metric


class NoCountPaginator(Paginator):
    @property
    def count(self):
        return 00000


class MetricAdmin(ReadOnlyMixin, admin.ModelAdmin):
    search_fields = [
        "name",
    ]


class GeographyAdmin(ReadOnlyMixin, admin.ModelAdmin):
    search_fields = [
        "name"
    ]


class CoreTimeseriesAdmin(ReadOnlyMixin, admin.ModelAdmin):
    date_hierarchy = "date"
    paginator = NoCountPaginator
    # show_facets = admin.ShowFacets.ALWAYS

    list_filter = [
        "metric",
        "age",
        "sex",
        "stratum",
        "geography",
        "geography__geography_type",
        "date",
    ]

    search_fields = [
        "geography__name",
        "metric__name",
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
    paginator = NoCountPaginator
    list_filter = [
        "metric",
        "age",
        "sex",
        "stratum",
        "geography",
        "geography__geography_type",
    ]

    search_fields = [
        "geography__name",
        "metric__name",
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
