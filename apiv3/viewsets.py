from rest_framework import viewsets

from apiv3.models import WeeklyTimeSeries
from apiv3.serializers import WeeklyTimeSeriesSerializer


class WeeklyTimeSeriesViewSet(viewsets.ModelViewSet):
    queryset = WeeklyTimeSeries.objects.all()
    serializer_class = WeeklyTimeSeriesSerializer

