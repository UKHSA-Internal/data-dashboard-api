from typing import List

from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
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
    TopicDetailSerializer,
    TopicListSerializer,
)

PUBLIC_API_TAG = "public-api"


class BaseNestedAPITimeSeriesView(GenericAPIView):
    queryset = APITimeSeries.objects.all()

    @property
    def lookup_field(self):
        raise NotImplementedError()

    @property
    def serializer_class(self):
        raise NotImplementedError()

    def _build_request_serializer(self, request: Request) -> APITimeSeriesRequestSerializer:
        serializer_context = {"request": request, "lookup_field": self.lookup_field}
        return APITimeSeriesRequestSerializer(context=serializer_context)

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request: Request, *args, **kwargs) -> Response:
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
    This endpoint returns a list of all available **themes** and hyperlinks to their corresponding detail view.

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
    This endpoint returns a list of all available **sub_themes** and hyperlinks to their corresponding detail view.

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


class TopicListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available **topics** and hyperlinks to their corresponding detail view.

    The `topic` field is positioned 1 step below `sub_theme`.

    A `topic` is the name of the topic/threat e.g. **COVID-19**
    """

    permission_classes = [HasAPIKey]
    lookup_field = "topic"
    serializer_class = TopicListSerializer


class TopicDetailView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns information about this specific `topic`
    and a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **geography_type**.
    """

    permission_classes = [HasAPIKey]
    lookup_field = "topic"
    serializer_class = TopicDetailSerializer


class PublicAPIRootView(APIView):
    """
    This is the root of the hyperlinked browsable timeseries API.

    From here you can use the `links` field to guide you to the data that you need.

    Whereby the `themes` field is a hyperlink to all the available **themes**.

    ---

    The data is hierarchical and is structured as follows:

    - -> `theme` - The largest topical subgroup e.g. **infectious_disease**

    - ---> `sub_theme` - A Topical subgroup e.g. **respiratory**

    - -----> `topic` - The name of the topic e.g. **COVID-19**

    - -------> `geography_type` - The type of geography e.g. **Nation**

    - ---------> `geography` - The name of geography associated with metric  e.g. **London**

    - -----------> `metric` - The name of the metric being queried for e.g. **new_cases_daily**

    - -------------> `timeseries` - The final slice of data, which will allow for further filtering via query parameters

    ---

    For example, items stated in bold above would produce the following full URL:

    ```
    .../themes/infectious_disease/sub_themes/respiratory/topics/COVID-19/geography_types/Nation/geographies/London/metrics/new_cases_daily/
    ```

    Note the overall structure of the URL.
    The category is required in plural form, followed by the detail of associated entity.

    For example, `/themes/` is the plural of `theme`.
    This would then be followed by the referring entity, **infectious_disease**

    ---

    The final step in the hierarchy is the `timeseries` endpoint.

    Which will provide the slice of data according to the selected URL parameters.

    At that point, additional query parameters are provided for further granularity and filtering of the data.

    """
    permission_classes = [HasAPIKey]
    name = "Public API Root"

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request, format=None):
        data = {
            "links": {
                "themes": reverse("theme-list", request=request, format=format),
            }
        }

        return Response(data)
