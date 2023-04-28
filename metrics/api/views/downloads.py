from typing import List, Dict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from metrics.api.serializers import APITimeSeriesSerializer, ChartsSerializer
from metrics.data.models.api_models import APITimeSeries
from django.http import HttpResponse

from metrics.domain.exports.csv import write_data_to_csv


from metrics.data.access.api_models import create_filters


class DownloadsViewSet(viewsets.ModelViewSet):
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
        "date_from",
        "dt",
    ]

    permission_classes = []
    renderer_classes = (CoreJSONRenderer,)

    def _get_queryset(self):
        all_queries: List[Dict[str, str]] = create_filters(
            filterset_fields=self.filterset_fields,
            plots=self.request.data["plots"],
        )

        # Fire off first query
        queryset = self.queryset.filter(**all_queries[0])

        # Now do the rest of the queries and join the results to the first one
        for query in all_queries[1:]:
            queryset = queryset | self.queryset.filter(**query)

        return queryset

    @action(detail=False, methods=["POST"])
    def json(self, request, *args, **kwargs):
        queryset = self._get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=ChartsSerializer)
    @action(detail=False, methods=["POST"])
    def csv(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="mymodel.csv"'

        queryset = self._get_queryset()
        response = write_data_to_csv(file=response, api_time_series=queryset)

        return response
