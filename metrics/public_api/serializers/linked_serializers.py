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
        view_name="sub_theme-detail",
        lookup_field="sub_theme",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )
