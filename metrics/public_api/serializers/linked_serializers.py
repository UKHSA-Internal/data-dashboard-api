from rest_framework.fields import CharField
from rest_framework.serializers import HyperlinkedIdentityField, Serializer
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField


class ThemeListSerializer(Serializer):
    name = CharField()
    link = HyperlinkedIdentityField(
        read_only=True,
        view_name="theme-detail",
        lookup_field="theme",
    )


class ThemeDetailSerializer(Serializer):
    information = CharField()
    sub_themes = HyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-list",
        lookup_field="theme",
    )


class SubThemeListSerializer(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-detail",
        lookup_field="sub_theme",
        parent_lookup_kwargs={"theme": "theme"},
    )


class SubThemeDetailSerializer(Serializer):
    information = CharField()
    topics = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-list",
        lookup_field="sub_theme",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicListSerializer(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-detail",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicDetailSerializer(Serializer):
    information = CharField()
    geography_types = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-list",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
        },
    )


class GeographyTypeListSerializer(Serializer):
    name = CharField()
    link = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-detail",
        lookup_field="geography_type",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
        },
    )


class GeographyTypeDetailSerializer(Serializer):
    information = CharField()
    geography_types = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name="geography_type-detail",
        lookup_field="geography_type",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
            "topic": "topic",
            "geography_type": "geography_type",
        },
    )
