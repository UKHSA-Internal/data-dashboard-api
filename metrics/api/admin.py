from django.contrib import admin

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreHeadline
from metrics.data.models.core_models.timeseries import CoreTimeSeries
from metrics.data.models.rbac_models import RBACGroupPermission, RBACPermission


@admin.register(RBACGroupPermission)
class RBACGroupPermissionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "group_id",
    ]
    list_per_page = 50
    list_max_show_all = 1000
    search_fields = ["name"]
    filter_horizontal = ["permissions"]


@admin.register(RBACPermission)
class RBACPermissionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "theme",
        "sub_theme__name",
        "topic",
        "metric",
        "geography_type",
        "geography",
    ]
    list_filter = [
        "theme",
        "sub_theme",
        "topic",
        "metric",
        "geography_type",
    ]
    list_per_page = 50
    list_max_show_all = 1000
    search_fields = [
        "theme__name",
        "sub_theme__name",
        "topic__name",
        "metric__name",
        "geography_type__name",
        "geography__name",
    ]
    search_help_text = (
        "Search by name, theme, sub_theme, topic, metric, "
        "geography type, or geography"
    )


@admin.register(APITimeSeries)
class APITimeSeriesAdmin(admin.ModelAdmin):
    list_display = [
        "theme",
        "sub_theme",
        "topic",
        "geography_code",
        "geography",
        "metric_value",
        "sex",
        "age",
        "epiweek",
        "date",
    ]
    list_filter = [
        "date",
        "theme",
        "is_public",
        "embargo",
        "in_reporting_delay_period",
        "refresh_date",
    ]
    ordering = ["-date"]
    list_per_page = 50
    list_max_show_all = 1000


@admin.register(CoreHeadline)
class CoreHeadlineAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "metric",
        "geography",
        "stratum",
        "age",
        "sex",
        "period_start",
        "period_end",
        "metric_value",
        "refresh_date",
        "embargo",
    ]
    list_filter = [
        "refresh_date",
        "embargo",
        "period_start",
        "period_end",
    ]
    list_select_related = ["metric", "geography", "stratum", "age"]
    list_per_page = 50
    list_max_show_all = 1000
    search_fields = ["geography__name", "geography__geography_type__name"]
    search_help_text = "Search by geography name or geography type"


@admin.register(CoreTimeSeries)
class CoreTimeSeriesAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "metric",
        "metric_frequency",
        "metric_value",
        "geography",
        "stratum",
        "metric_value",
        "age",
        "sex",
        "year",
        "month",
        "epiweek",
        "date",
        "refresh_date",
        "embargo",
        "in_reporting_delay_period",
    ]
    list_filter = [
        "date",
        "refresh_date",
        "embargo",
    ]
    list_select_related = ["metric", "geography", "stratum", "age"]
    list_per_page = 50
    list_max_show_all = 1000
    search_fields = ["geography__name", "geography__geography_type__name"]
    search_help_text = "Search by geography name or geography type"
