import io
from typing import Dict, List

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import APITimeSeriesSerializer, DownloadsSerializer
from metrics.data.access.api_models import validate_query_filters
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.exports.csv import write_data_to_csv


class DownloadsView(APIView):
    queryset = APITimeSeries.objects.all().order_by("dt")
    serializer_class = APITimeSeriesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "period",
        "theme",
        "sub_theme",
        "topic",
        "geography_type",
        "geography",
        "metric",
        "stratum",
        "sex",
        "year",
        "epiweek",
        "date_from",
        "date_to",
    ]
    permission_classes = [HasAPIKey]

    renderer_classes = (CoreJSONRenderer,)

    def _get_queryset(self):
        all_query_filters: List[Dict[str, str]] = validate_query_filters(
            possible_fields=self.filterset_fields,
            plots=self.request.data["plots"],
        )

        # Fire off first query
        queryset = self.queryset.filter(**all_query_filters[0])

        # Now do the rest of the queries and join the results to the first one
        for query in all_query_filters[1:]:
            queryset = queryset | self.queryset.filter(**query)

        return queryset

    def _handle_json(self) -> Response:
        # Return the requested data in json format
        queryset = self._get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def _handle_csv(self) -> io.StringIO:
        # Return the requested data in csv format
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="mymodel.csv"'

        queryset = self._get_queryset()
        response = write_data_to_csv(file=response, api_time_series=queryset)
        return response

    @extend_schema(request=DownloadsSerializer)
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
        | `metric`          | The name of the metric being queried for                                  | `new_cases_7day_avg`      |
        | `stratum`         | The smallest subgroup a metric can be broken down into                    | `0_4`                     |
        | `sex`             | The sex for those metrics that are broken down by sex                     | `M`                       |
        | `date_from`       | The date to pull the data from                                            | `2020-01-20`              |
        | `date_to`         | The date to pull the data up until                                        | `2023-01-20`              |
        """

        request_serializer = DownloadsSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        file_format = request_serializer.data["file_format"]

        if file_format == "json":
            return self._handle_json()
        elif file_format == "csv":
            return self._handle_csv()
