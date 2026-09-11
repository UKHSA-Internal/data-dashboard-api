from public_api.version.v3.serializers.linked_serializers import (
    GeographyDetailSerializerv3,
    GeographyListSerializerv3,
    GeographyTypeDetailSerializerv3,
    GeographyTypeListSerializerv3,
    MetricListSerializerv3,
    SubThemeDetailSerializerv3,
    SubThemeListSerializerv3,
    ThemeDetailSerializerv3,
    ThemeListSerializerv3,
    TopicDetailSerializerv3,
    TopicListSerializerv3,
)
from public_api.version.v3.views.base import BaseNestedAPIViewV3


class ThemeListViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a list of all available **themes** and hyperlinks to their corresponding detail view.

    A `theme` is the largest topical subgroup e.g. **infectious_disease**.
    """

    permission_classes = []
    lookup_field = "theme"
    serializer_class = ThemeListSerializerv3


class ThemeDetailViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **sub_themes**.
    """

    permission_classes = []
    lookup_field = "theme"
    serializer_class = ThemeDetailSerializerv3


class SubThemeListViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a list of all available **sub_themes** and hyperlinks to their corresponding detail view.

    The `sub_theme` field is positioned 1 step below `theme`.

    A `sub_theme` is a topical subgroup  e.g. **respiratory**
    """

    permission_classes = []
    lookup_field = "sub_theme"
    serializer_class = SubThemeListSerializerv3


class SubThemeDetailViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **topics**.
    """

    permission_classes = []
    lookup_field = "sub_theme"
    serializer_class = SubThemeDetailSerializerv3


class TopicListViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a list of all available **topics** and hyperlinks to their corresponding detail view.

    The `topic` field is positioned 1 step below `sub_theme`.

    A `topic` is the name of the topic/threat e.g. **COVID-19**
    """

    permission_classes = []
    lookup_field = "topic"
    serializer_class = TopicListSerializerv3


class TopicDetailViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **geography_type**.
    """

    permission_classes = []
    lookup_field = "topic"
    serializer_class = TopicDetailSerializerv3


class GeographyTypeListViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a list of all available geography types and hyperlinks to their corresponding detail view.

    The `geography_type` field is positioned 1 step below `topic`.

    A `geography_type` is the type of geography e.g. **Nation**

    """

    permission_classes = []
    lookup_field = "geography_type"
    serializer_class = GeographyTypeListSerializerv3


class GeographyTypeDetailViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **geography**.

    """

    permission_classes = []
    lookup_field = "geography_type"
    serializer_class = GeographyTypeDetailSerializerv3


class GeographyListViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a list of all available geographies and hyperlinks to their corresponding detail view.

    The `geography` field is positioned 1 step below `geography_type`.

    A `geography` is the value of the geography e.g. **London**

    """

    permission_classes = []
    lookup_field = "geography"
    serializer_class = GeographyListSerializerv3


class GeographyDetailViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a hyperlink to the next step in the data hierarchy.

    In this case, the next step in the data hierarchy is **metric**.

    """

    permission_classes = []
    lookup_field = "geography"
    serializer_class = GeographyDetailSerializerv3


class MetricListViewV3(BaseNestedAPIViewV3):
    """
    This endpoint returns a list of all available metrics and hyperlinks to their corresponding detail view.

    The `metric` field is positioned 1 step below `geography`.

    A `metric` is the name of the metric being queried for e.g. **COVID-19_deaths_ONSByDay**

    """

    permission_classes = []
    lookup_field = "metric"
    serializer_class = MetricListSerializerv3
