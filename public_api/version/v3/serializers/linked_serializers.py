from rest_framework.fields import CharField
from rest_framework.serializers import HyperlinkedIdentityField, Serializer
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField


class ThemeListSerializerv3(Serializer):
    name = CharField()
    link = HyperlinkedIdentityField(
        read_only=True,
        view_name="theme-detail-v3",
        lookup_field="theme",
    )


class ThemeDetailSerializerv3(Serializer):
    sub_themes = HyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-list-v3",
        lookup_field="theme",
    )


class SubThemeListSerializerv3(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-detail-v3",
        lookup_field="sub_theme",
        parent_lookup_kwargs={"theme": "theme"},
    )


class SubThemeDetailSerializerv3(Serializer):
    topics = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-list-v3",
        lookup_field="sub_theme",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicListSerializerv3(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-detail-v3",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicDetailSerializerv3(Serializer):
    geography_types = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-list-v3",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
        },
    )


class GeographyTypeListSerializerv3(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-detail-v3",
        lookup_field="geography_type",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
        },
    )


class GeographyTypeDetailSerializerv3(Serializer):
    geographies = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography-list-v3",
        lookup_field="geography_type",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
        },
    )


class GeographyListSerializerv3(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography-detail-v3",
        lookup_field="geography",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
        },
    )


class GeographyDetailSerializerv3(Serializer):
    metrics = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="metric-list-v3",
        lookup_field="geography",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
            "geography": "geography",
        },
    )


class MetricListSerializerv3(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="timeseries-list-v3",
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
