from django.contrib import admin
from .mixins import ReadOnlyMixin


class APITimeseriesAdmin(ReadOnlyMixin, admin.ModelAdmin):
    list_filter = [
        "metric",
        "age",
        "sex",
        "stratum",
        "geography",
        "geography_type",
        "date",
    ]

    # search_fields = [
    #     "geography"
    # ]
    #
    # autocomplete_fields = [
    #     "geography",
    # ]

    list_display = [
        "metric_frequency",
        "age",
        "month",
        "metric",
        "metric_value",
        "metric_group",
        "geography_code",
        "geography",
        "geography_type",
        "stratum",
        "sex",
        "year",
        "epiweek",
        "refresh_date",
        "date",
        "embargo",
        "in_reporting_delay_period",
    ]

    # def get_queryset(self, request):
    #     query_set = super().get_queryset(request)
    #     start_date = (datetime.now() - timedelta(days=91)).strftime("%Y-%m-%d")
    #     end_date = (datetime.now()).strftime("%Y-%m-%d")
    #
    #     return query_set.filter(date__gte=start_date, date__lte=end_date)
