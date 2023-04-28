from http import HTTPStatus
from typing import Dict, List

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers import APITimeSeriesSerializer
from metrics.data.access.api_models import create_filters
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.exports.csv import write_data_to_csv


class DownloadsView(APIView):
    queryset = APITimeSeries.objects.all().order_by("dt")
    serializer_class = APITimeSeriesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "theme",
        "sub_theme",
        "topic",
        "geography_type",
        "geography",
        "metric",
        "stratum",
        "sex",
        "dt",
    ]

    # All the fields you can filter by
    possible_fields = filterset_fields + ["date_from"]

    permission_classes = []
    renderer_classes = (CoreJSONRenderer,)

    def _get_queryset(self):
        all_queries: List[Dict[str, str]] = create_filters(
            possible_fields=self.possible_fields,
            plots=self.request.data["plots"],
        )

        # Fire off first query
        queryset = self.queryset.filter(**all_queries[0])

        # Now do the rest of the queries and join the results to the first one
        for query in all_queries[1:]:
            queryset = queryset | self.queryset.filter(**query)

        return queryset

    def post(self, request, *args, **kwargs):
        """This endpoint will return the query output in json/csv format

        It is designed to be used alongside the Charts endpoint to enable the user to dump the data for use elsewhere

        Multiple queries can be added as an array of objects in the request body.

        A `format` parameter **must** be supplied and set to either `json` or `csv`.
        This `format` parameter applies to the whole of the output, it is not plot specific

        This function will recognise the following set of payload parameters for each plot. None are mandatory:

        | Parameter name    | Description                                                               | Example                   |
        |-------------------|---------------------------------------------------------------------------|---------------------------|
        | `theme`           | The theme                                                                 | infectious_disease        |
        | `sub_theme`       | The sub-theme                                                             | respiratory               |
        | `topic`           | The name of the disease/threat                                            | COVID-19                  |
        | `geography_type`  | The type of geographical categorisation to apply any data filtering to    | Nation                    |
        | `geography`       | The geography constraints to apply any data filtering to                  | London                    |
        | `metric`          | The name of the metric being queried for                                  | new_cases_7day_avg        |
        | `stratum`         | The smallest subgroup a metric can be broken down into                    | 0_4                       |
        | `sex`             | The sex for those mwetrics that are broken down by sex                    | M                         |
        | `date_from`       | The date to pull the data from                                            | "2023-01-20"              |
        | `dt`              | The date to pull the data for                                             | "2023-01-20"              |

        So the full payload to this endpoint could look like the following:

        ```
            {
             "format": "json",
             "plots": [
                {
                  "topic": "COVID-19",
                  "metric": "new_cases_daily",
                  "chart_type": "bar",              #any unrecognised parameters will be ignored
                  "date_from": "2020-03-02"
                },
                {
                  "topic": "COVID-19",
                  "metric": ["new_cases_7day_avg", "new_deaths_7day_avg"],
                  "dt": "2023-03-02"
                }
              ]
            }
        ```
        """
        queryset = self._get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        data_format = self.request.data.get("format")

        if data_format == "json":
            return Response(serializer.data)
        elif data_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="mymodel.csv"'

            queryset = self._get_queryset()
            response = write_data_to_csv(file=response, api_time_series=queryset)

            return response

        return Response(
            status=HTTPStatus.BAD_REQUEST,
            data={"error_message": "format of json or csv not specified"},
        )
