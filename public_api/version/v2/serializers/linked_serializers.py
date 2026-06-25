from rest_framework.fields import CharField
from rest_framework.serializers import HyperlinkedIdentityField, Serializer
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField


class ThemeListSerializerv2(Serializer):
    name = CharField()
    link = HyperlinkedIdentityField(
        read_only=True,
        view_name="theme-detail-v2",
        lookup_field="theme",
    )


class ThemeDetailSerializerv2(Serializer):
    sub_themes = HyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-list-v2",
        lookup_field="theme",
    )


class SubThemeListSerializerv2(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-detail-v2",
        lookup_field="sub_theme",
        parent_lookup_kwargs={"theme": "theme"},
    )


class SubThemeDetailSerializerv2(Serializer):
    topics = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-list-v2",
        lookup_field="sub_theme",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicListSerializerv2(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-detail-v2",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicDetailSerializerv2(Serializer):
    geography_types = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-list-v2",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
        },
    )


class GeographyTypeListSerializerv2(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-detail-v2",
        lookup_field="geography_type",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
        },
    )


class GeographyTypeDetailSerializerv2(Serializer):
    geographies = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography-list-v2",
        lookup_field="geography_type",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
        },
    )


class GeographyListSerializerv2(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography-detail-v2",
        lookup_field="geography",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
        },
    )


class GeographyDetailSerializerv2(Serializer):
    metrics = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="metric-list-v2",
        lookup_field="geography",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
            "geography": "geography",
        },
    )


class MetricListSerializerv2(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="timeseries-list-v2",
        lookup_field="metric",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
            "geography": "geography",
            "metric": "metric",
        },
    )
