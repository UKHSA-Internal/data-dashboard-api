from typing import List

from django.views.decorators.http import require_http_methods
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_api_key.permissions import HasAPIKey

from metrics.data.models.api_models import APITimeSeries
from metrics.public_api.serializers.api_time_series_request_serializer import (
    APITimeSeriesDTO,
    APITimeSeriesRequestSerializer,
)
from metrics.public_api.serializers.linked_serializers import (
    SubThemeDetailSerializer,
    SubThemeListSerializer,
    ThemeDetailSerializer,
    ThemeListSerializer,
)


class BaseNestedAPITimeSeriesView(generics.GenericAPIView):
    queryset = APITimeSeries.objects.all()

    @property
    def lookup_field(self):
        raise NotImplementedError()

    @property
    def serializer_class(self):
        raise NotImplementedError()

    def _build_request_serializer(self, request) -> APITimeSeriesRequestSerializer:
        serializer_context = {"request": request, "lookup_field": self.lookup_field}
        return APITimeSeriesRequestSerializer(context=serializer_context)

    def get(self, request, *args, **kwargs) -> Response:
        serializer: APITimeSeriesRequestSerializer = self._build_request_serializer(
            request=request
        )
        timeseries_dto_slice: List[
            APITimeSeriesDTO
        ] = serializer.build_timeseries_dto_slice()

        serializer = self.get_serializer(timeseries_dto_slice, many=True)
        return Response(serializer.data)


class ThemeListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available themes and hyperlinks to their corresponding detail view.

    A `theme` is the largest topical subgroup e.g. **infectious_disease**.
    """

    permission_classes = [HasAPIKey]
    lookup_field = "theme"
    serializer_class = ThemeListSerializer


class ThemeDetailView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns information about this specific `theme`
    and a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **sub_themes**.
    """

    permission_classes = [HasAPIKey]
    lookup_field = "theme"
    serializer_class = ThemeDetailSerializer


class SubThemeListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available sub_themes and hyperlinks to their corresponding detail view.

    The `sub_theme` field is positioned 1 step below `theme`.

    A `sub_theme` is a topical subgroup  e.g. **respiratory**
    """

    permission_classes = [HasAPIKey]
    lookup_field = "sub_theme"
    serializer_class = SubThemeListSerializer


class SubThemeDetailView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns information about this specific `sub_theme`
    and a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **topics**.
    """

    permission_classes = [HasAPIKey]
    lookup_field = "sub_theme"
    serializer_class = SubThemeDetailSerializer


@api_view(["GET"])
@require_http_methods(["GET"])
def public_api_root(request, format=None):
    data = {
        "links": {
            "themes": reverse("theme-list", request=request, format=format),
        }
    }

    return Response(data)
