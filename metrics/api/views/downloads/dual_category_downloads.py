import io
from http import HTTPStatus

from django.http import HttpResponse
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers import DualCategoryDownloadSerializer
from metrics.api.views.downloads.common import DOWNLOADS_API_TAG
from metrics.api.views.downloads.single_category_downloads import (
    SingleCategoryDownloadsView,
)
from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.domain.common.utils import DataSourceFileType
from metrics.domain.exports.dual_category_output import (
    build_dual_category_csv_headers,
    pivot_dual_category_download_rows,
    write_dual_category_data_to_csv,
)
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)
from metrics.interfaces.downloads.dual_category.access import (
    get_dual_category_downloads_data,
)
from metrics.interfaces.plots.access import DataNotFoundForAnyPlotError

EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD = {
    "file_format": "json",
    "x_axis": "age",
    "chart_type": "stacked_bar",
    "y_axis": "metric",
    "primary_field_values": [
        "00-01",
        "01-04",
        "05-09",
        "05-11",
        "05-14",
        "10-14",
    ],
    "static_fields": {
        "topic": "Lead",
        "metric": "lead_headline_ratesByAgeSex",
        "geography": "England",
        "geography_type": "Nation",
        "sex": "all",
        "age": "all",
        "stratum": "default",
        "date_from": "2020-05-21",
        "date_to": "2026-05-21",
    },
    "secondary_category": "sex",
    "segments": [
        {
            "secondary_field_value": "f",
            "colour": "COLOUR_1_DARK_BLUE",
            "label": "",
        },
        {
            "secondary_field_value": "m",
            "colour": "COLOUR_1_DARK_BLUE",
            "label": "Males",
        },
    ],
}


class DualCategoryDownloadsView(SingleCategoryDownloadsView):
    def _get_serializer_class(
        self, queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet, metric_group: str
    ):
        """Return serializer for dual-category downloads without confidence intervals.

        Args:
            queryset: Merged queryset for the requested plots.
            metric_group: Metric group used to select the serializer type.

        Returns:
            Headline or timeseries serializer for the download export.
        """
        if DataSourceFileType[metric_group].is_headline:
            return self.headline_serializer_class(
                queryset,
                many=True,
                context={"confidence_intervals": False},
            )

        return super()._get_serializer_class(
            queryset=queryset,
            metric_group=metric_group,
        )

    def _pivot_queryset_data(
        self,
        *,
        queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet,
        chart_plot_models: DualCategoryDownloadRequestParams,
    ) -> list[dict]:
        """Serialize and pivot queryset data for dual-category download export.

        Args:
            queryset: Merged queryset for the requested plots.
            chart_plot_models: Validated dual-category download request parameters.

        Returns:
            Pivoted rows ready for JSON or CSV export.
        """
        serializer = self._get_serializer_class(
            queryset=queryset,
            metric_group=chart_plot_models.metric_group,
        )

        return pivot_dual_category_download_rows(
            rows=serializer.data,
            x_axis=chart_plot_models.x_axis,
            secondary_category=chart_plot_models.secondary_category,
        )

    def _handle_json(
        self,
        *,
        queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet,
        chart_plot_models: DualCategoryDownloadRequestParams,
    ) -> Response:
        """Return pivoted dual-category download data as a JSON attachment.

        Args:
            queryset: Merged queryset for the requested plots.
            chart_plot_models: Validated dual-category download request parameters.

        Returns:
            JSON attachment response containing pivoted download rows.
        """
        pivoted_rows = self._pivot_queryset_data(
            queryset=queryset,
            chart_plot_models=chart_plot_models,
        )
        response = Response(pivoted_rows)
        response["Content-Type"] = "application/json"
        response["Content-Disposition"] = (
            "attachment; filename=dual_category_download.json"
        )
        return response

    def _handle_csv(
        self,
        *,
        queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet,
        chart_plot_models: DualCategoryDownloadRequestParams,
    ) -> io.StringIO:
        """Return pivoted dual-category download data as a CSV attachment.

        Args:
            queryset: Merged queryset for the requested plots.
            chart_plot_models: Validated dual-category download request parameters.

        Returns:
            CSV attachment response containing pivoted download rows.
        """
        pivoted_rows = self._pivot_queryset_data(
            queryset=queryset,
            chart_plot_models=chart_plot_models,
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="dual_category_download.csv"'
        )
        is_headline = DataSourceFileType[chart_plot_models.metric_group].is_headline
        headers = build_dual_category_csv_headers(
            is_headline=is_headline,
            x_axis=chart_plot_models.x_axis,
            secondary_category=chart_plot_models.secondary_category,
            segment_secondary_values=chart_plot_models.segment_secondary_values,
        )
        return write_dual_category_data_to_csv(
            file=response,
            rows=pivoted_rows,
            headers=headers,
        )

    @extend_schema(
        request=DualCategoryDownloadSerializer,
        tags=[DOWNLOADS_API_TAG],
        examples=[
            OpenApiExample(
                name="Lead age-sex headline example",
                value=EXAMPLE_DUAL_CATEGORY_DOWNLOAD_REQUEST_PAYLOAD,
                request_only=True,
            )
        ],
    )
    @cache_response()
    @require_authorisation
    def post(self, request, *args, **kwargs):
        """Handle a dual-category download request and return JSON or CSV data.

        Args:
            request: The incoming download request payload.

        Returns:
            JSON or CSV attachment response containing pivoted download data.
        """
        request_serializer = DualCategoryDownloadSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        file_format: str = request_serializer.data["file_format"]
        chart_plot_models: DualCategoryDownloadRequestParams = (
            request_serializer.to_models(request=request)
        )

        try:
            queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet = (
                get_dual_category_downloads_data(
                    download_request_params=chart_plot_models,
                )
            )
        except DataNotFoundForAnyPlotError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        match file_format:
            case "json":
                return self._handle_json(
                    queryset=queryset,
                    chart_plot_models=chart_plot_models,
                )
            case "csv":
                return self._handle_csv(
                    queryset=queryset,
                    chart_plot_models=chart_plot_models,
                )
