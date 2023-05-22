from rest_framework.fields import CharField
from rest_framework.serializers import HyperlinkedIdentityField, Serializer


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
        view_name="theme-detail",  # Replace with sub_theme-list when available
        lookup_field="theme",
    )
