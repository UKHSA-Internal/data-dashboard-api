from django.http.response import HttpResponse
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.api.views.downloads.common import DOWNLOADS_API_TAG
from metrics.api.views.downloads.single_category_downloads import DownloadsView
from metrics.api.views.downloads.subplot_downloads.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.domain.common.utils import DataSourceFileType
from metrics.domain.exports.csv_output import (
    write_data_to_csv,
    write_headline_data_to_csv,
)
from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.downloads import access
from metrics.interfaces.plots.access import DataNotFoundForAnyPlotError

DEFAULT_VALUE_ERROR_MESSAGE = "Invalid metric_group provided"


class SubplotDownloadsView(DownloadsView):
    @extend_schema(
        request=SubplotChartRequestSerializer,
        examples=[
            OpenApiExample(
                name="MMR1 (2 years)", value=REQUEST_PAYLOAD_EXAMPLE, request_only=True
            )
        ],
        tags=[DOWNLOADS_API_TAG],
    )
    @cache_response()
    @require_authorisation
    def post(self, request, *args, **kwargs):
        request_serializer = SubplotChartRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        file_format: str = request_serializer.data["file_format"]
        request.data["file_format"] = "svg"

        subplot_chart_parameters: SubplotChartRequestParameters = (
            request_serializer.to_models(request=request)
        )
        charts_request_param_models: list[ChartRequestParams] = (
            subplot_chart_parameters.output_payload_for_tables()
        )

        if file_format == "csv":
            return self._handle_csv(
                charts_request_param_models=charts_request_param_models
            )
        return self._handle_json(
            charts_request_param_models=charts_request_param_models
        )

    def _handle_json(
        self, *, charts_request_param_models: list[ChartRequestParams]
    ) -> Response:
        data = []
        for charts_request_param in charts_request_param_models:
            try:
                queryset: CoreTimeSeriesQuerySet = access.get_downloads_data(
                    chart_plots=charts_request_param
                )
            except DataNotFoundForAnyPlotError:
                continue

            serializer = self._get_serializer_class(
                queryset=queryset, metric_group=charts_request_param.metric_group
            )
            data.append(serializer.data)

        response = Response(data)
        response["Content-Type"] = "application/json"
        response["Content-Disposition"] = "attachment; filename=chart_download.json"
        return response

    def _handle_csv(
        self, *, charts_request_param_models: list[ChartRequestParams]
    ) -> HttpResponse:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="charts-download.csv"'

        for index, charts_request_param in enumerate(charts_request_param_models, 1):
            queryset: CoreTimeSeriesQuerySet = access.get_downloads_data(
                chart_plots=charts_request_param
            )
            metric_group: str = charts_request_param.metric_group

            headers = [""] * 12 if index > 1 else None

            if DataSourceFileType[metric_group].is_headline:
                serializer = self._get_serializer_class(
                    queryset=queryset, metric_group=metric_group
                )
                return write_headline_data_to_csv(
                    file=response, headers=headers, core_headline_data=serializer.data
                )
            write_data_to_csv(
                file=response, headers=headers, core_time_series_queryset=queryset
            )

        return response
