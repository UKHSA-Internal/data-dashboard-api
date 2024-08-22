from public_api.serializers.linked_serializers import (
    GeographyListSerializer,
    GeographyTypeListSerializer,
    MetricListSerializer,
    SubThemeListSerializer,
    ThemeListSerializer,
    TopicListSerializer,
)
from public_api.views.base import BaseNestedAPITimeSeriesView


class ThemeListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available **themes** and hyperlinks to their corresponding detail view.

    A `theme` is the largest topical subgroup e.g. **infectious_disease**.
    """

    permission_classes = []
    lookup_field = "theme"
    serializer_class = ThemeListSerializer


class SubThemeListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available **sub_themes** and hyperlinks to their corresponding detail view.

    The `sub_theme` field is positioned 1 step below `theme`.

    A `sub_theme` is a topical subgroup  e.g. **respiratory**
    """

    permission_classes = []
    lookup_field = "sub_theme"
    serializer_class = SubThemeListSerializer


class TopicListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available **topics** and hyperlinks to their corresponding detail view.

    The `topic` field is positioned 1 step below `sub_theme`.

    A `topic` is the name of the topic/threat e.g. **COVID-19**
    """

    permission_classes = []
    lookup_field = "topic"
    serializer_class = TopicListSerializer


class GeographyTypeListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available geography types and hyperlinks to their corresponding detail view.

    The `geography_type` field is positioned 1 step below `topic`.

    A `geography_type` is the type of geography e.g. **Nation**

    """

    permission_classes = []
    lookup_field = "geography_type"
    serializer_class = GeographyTypeListSerializer


class GeographyListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available geographies and hyperlinks to their corresponding detail view.

    The `geography` field is positioned 1 step below `geography_type`.

    A `geography` is the value of the geography e.g. **London**

    """

    permission_classes = []
    lookup_field = "geography"
    serializer_class = GeographyListSerializer


class MetricListView(BaseNestedAPITimeSeriesView):
    """
    This endpoint returns a list of all available metrics and hyperlinks to their corresponding detail view.

    The `metric` field is positioned 1 step below `geography`.

    A `metric` is the name of the metric being queried for e.g. **COVID-19_deaths_ONSByDay**

    """

    permission_classes = []
    lookup_field = "metric"
    serializer_class = MetricListSerializer
