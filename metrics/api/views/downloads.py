import io
import logging
from http import HTTPStatus

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers import (
    BulkDownloadsSerializer,
    CoreHeadlineSerializer,
    CoreTimeSeriesSerializer,
    DownloadsSerializer,
)
from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.domain.bulk_downloads.get_downloads_archive import (
    get_bulk_downloads_archive,
)
from metrics.domain.common.utils import DataSourceFileType
from metrics.domain.exports.csv_output import (
    write_data_to_csv,
    write_headline_data_to_csv,
)
from metrics.interfaces.downloads import access
from metrics.interfaces.plots.access import DataNotFoundForAnyPlotError

DOWNLOADS_API_TAG = "downloads"

logger = logging.getLogger(__name__)

DEFAULT_VALUE_ERROR_MESSAGE = "Invalid metric_group provided"


class DownloadsView(APIView):
    timeseries_serializer_class = CoreTimeSeriesSerializer
    headline_serializer_class = CoreHeadlineSerializer
    permission_classes = []

    renderer_classes = (JSONOpenAPIRenderer,)

    def _get_serializer_class(
        self, queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet, metric_group: str
    ) -> CoreHeadlineSerializer | CoreTimeSeriesSerializer:
        """Returns the appropriate serializer class based on the
            provided metric_group.

        Returns:
            a serializer based on the provided `metric_group`
            Eg. `CoreTimeSeriesSerializer` or `CoreHeadlineSerializer`
        """
        try:
            if DataSourceFileType[metric_group].is_headline:
                return self.headline_serializer_class(queryset, many=True)

            if DataSourceFileType[metric_group].is_timeseries:
                return self.timeseries_serializer_class(queryset, many=True)

        except KeyError as error:
            raise ValueError(DEFAULT_VALUE_ERROR_MESSAGE) from error

    def _handle_json(
        self,
        *,
        queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet,
        metric_group: str,
    ) -> Response:
        # Return the requested data in json format
        serializer = self._get_serializer_class(
            queryset=queryset, metric_group=metric_group
        )

        response = Response(serializer.data)
        response["Content-Type"] = "application/json"
        response["Content-Disposition"] = "attachment; filename=chart_download.json"
        return response

    def _handle_csv(
        self,
        *,
        queryset: CoreTimeSeriesQuerySet | CoreHeadlineQuerySet,
        metric_group: str,
    ) -> io.StringIO:
        # Return the requested data in csv format
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="mymodel.csv"'

        serializer = self._get_serializer_class(
            queryset=queryset, metric_group=metric_group
        )

        if DataSourceFileType[metric_group].is_headline:
            return write_headline_data_to_csv(
                file=response, core_headline_data=serializer.data
            )

        return write_data_to_csv(file=response, core_time_series_queryset=queryset)

    @extend_schema(request=DownloadsSerializer, tags=[DOWNLOADS_API_TAG])
    @cache_response()
    @require_authorisation
    def post(self, request, *args, **kwargs):
        """This endpoint will return the query output in json/csv format

        It is designed to be used alongside the Charts endpoint to enable the user to dump the data for use elsewhere

        Multiple queries can be added as an array of objects in the request body.

        A `file_format` parameter **must** be supplied and set to either `json` or `csv`.
        This `file_format` parameter applies to the whole of the output, it is not plot specific

        This function will recognise the following set of payload parameters for each plot. None are mandatory:

        | Parameter name    | Description                                                               | Example                   |
        |-------------------|---------------------------------------------------------------------------|---------------------------|
        | `theme`           | The theme                                                                 | `infectious_disease`      |
        | `sub_theme`       | The sub-theme                                                             | `respiratory`             |
        | `topic`           | The name of the disease/threat                                            | `COVID-19`                |
        | `geography_type`  | The type of geographical categorisation to apply any data filtering to    | `Nation`                  |
        | `geography`       | The geography constraints to apply any data filtering to                  | `London`                  |
        | `metric`          | The name of the metric being queried for                                  | `COVID-19_deaths_ONSByDay`|
        | `stratum`         | The smallest subgroup a metric can be broken down into                    | `default`                 |
        | `sex`             | The sex for those metrics that are broken down by sex                     | `F`                       |
        | `age`             | The patient age band                                                      | 0_4                       |
        | `date_from`       | The date to pull the data from                                            | `2020-01-20`              |
        | `date_to`         | The date to pull the data up until                                        | `2023-01-20`              |

        """
        request_serializer = DownloadsSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        file_format: str = request_serializer.data["file_format"]
        chart_plot_models = request_serializer.to_models(request=request)

        try:
            queryset: CoreTimeSeriesQuerySet = access.get_downloads_data(
                chart_plots=chart_plot_models
            )
        except DataNotFoundForAnyPlotError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        match file_format:
            case "json":
                return self._handle_json(
                    queryset=queryset, metric_group=chart_plot_models.metric_group
                )
            case "csv":
                return self._handle_csv(
                    queryset=queryset, metric_group=chart_plot_models.metric_group
                )


class BulkDownloadsView(APIView):
    @classmethod
    @extend_schema(
        parameters=[BulkDownloadsSerializer],
        tags=[DOWNLOADS_API_TAG],
    )
    def get(cls, request, *args, **kwargs):
        """This endpoint can be used to get all downloads from the current dashboard and return them in a zip file

        Note this endpoint will return a zipfile containing a collection of folders based on page names, each
        folder will contain a series of csv or json files named after the charts currently published on the dashboard.

        # Main errors

        If any of the charts fail to be retrieved a 500 server error will be returned and the file
        will not be downloaded.

        This endpoint supports both csv and json format for its downloads
        this makes the 'file_format' parameter a required field
        not supplying this as a query parameter will result in a 400 Bad Request.

        """
        request_serializer = BulkDownloadsSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        file_format = request_serializer.data["file_format"]

        compressed_downloads = get_bulk_downloads_archive(file_format=file_format)

        response = HttpResponse(
            compressed_downloads["zip_file_data"], content_type="application/zip"
        )
        response["Content-Disposition"] = (
            f"attachment; filename={compressed_downloads['zip_file_name']}"
        )
        return response
