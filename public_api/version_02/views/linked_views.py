from public_api.version_02.serializers.linked_serializers import (
    GeographyDetailSerializerv2,
    GeographyListSerializerv2,
    GeographyTypeDetailSerializerv2,
    GeographyTypeListSerializerv2,
    MetricListSerializerv2,
    SubThemeDetailSerializerv2,
    SubThemeListSerializerv2,
    ThemeDetailSerializerv2,
    ThemeListSerializerv2,
    TopicDetailSerializerv2,
    TopicListSerializerv2,
)
from public_api.version_02.views.base import BaseNestedAPITimeSeriesViewV2


class ThemeListViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a list of all available **themes** and hyperlinks to their corresponding detail view.

    A `theme` is the largest topical subgroup e.g. **infectious_disease**.
    """

    permission_classes = []
    lookup_field = "theme"
    serializer_class = ThemeListSerializerv2


class ThemeDetailViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **sub_themes**.
    """

    permission_classes = []
    lookup_field = "theme"
    serializer_class = ThemeDetailSerializerv2


class SubThemeListViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a list of all available **sub_themes** and hyperlinks to their corresponding detail view.

    The `sub_theme` field is positioned 1 step below `theme`.

    A `sub_theme` is a topical subgroup  e.g. **respiratory**
    """

    permission_classes = []
    lookup_field = "sub_theme"
    serializer_class = SubThemeListSerializerv2


class SubThemeDetailViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **topics**.
    """

    permission_classes = []
    lookup_field = "sub_theme"
    serializer_class = SubThemeDetailSerializerv2


class TopicListViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a list of all available **topics** and hyperlinks to their corresponding detail view.

    The `topic` field is positioned 1 step below `sub_theme`.

    A `topic` is the name of the topic/threat e.g. **COVID-19**
    """

    permission_classes = []
    lookup_field = "topic"
    serializer_class = TopicListSerializerv2


class TopicDetailViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **geography_type**.
    """

    permission_classes = []
    lookup_field = "topic"
    serializer_class = TopicDetailSerializerv2


class GeographyTypeListViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a list of all available geography types and hyperlinks to their corresponding detail view.

    The `geography_type` field is positioned 1 step below `topic`.

    A `geography_type` is the type of geography e.g. **Nation**

    """

    permission_classes = []
    lookup_field = "geography_type"
    serializer_class = GeographyTypeListSerializerv2


class GeographyTypeDetailViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **geography**.

    """

    permission_classes = []
    lookup_field = "geography_type"
    serializer_class = GeographyTypeDetailSerializerv2


class GeographyListViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a list of all available geographies and hyperlinks to their corresponding detail view.

    The `geography` field is positioned 1 step below `geography_type`.

    A `geography` is the value of the geography e.g. **London**

    """

    permission_classes = []
    lookup_field = "geography"
    serializer_class = GeographyListSerializerv2


class GeographyDetailViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **metric**.

    """

    permission_classes = []
    lookup_field = "geography"
    serializer_class = GeographyDetailSerializerv2


class MetricListViewV2(BaseNestedAPITimeSeriesViewV2):
    """
    This endpoint returns a list of all available metrics and hyperlinks to their corresponding detail view.

    The `metric` field is positioned 1 step below `geography`.

    A `metric` is the name of the metric being queried for e.g. **COVID-19_deaths_ONSByDay**

    """

    permission_classes = []
    lookup_field = "metric"
    serializer_class = MetricListSerializerv2
