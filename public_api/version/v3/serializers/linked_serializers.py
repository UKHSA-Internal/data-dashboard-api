from functools import reduce

from rest_framework.fields import CharField
from rest_framework.serializers import HyperlinkedIdentityField, Serializer
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField


class PrefixedHyperlinkedIdentityField(HyperlinkedIdentityField):
    url_prefix = ""

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        url = obj.url_prefix + "-" + view_name
        return self.reverse(kwargs=kwargs, request=request, format=format, viewname=url)


class NestedPrefixedHyperlinkedIdentityField(NestedHyperlinkedIdentityField):
    url_prefix = ""

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None
        # default lookup from rest_framework.relations.HyperlinkedRelatedField
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}

        # multi-level lookup
        for parent_lookup_kwarg in list(self.parent_lookup_kwargs.keys()):
            underscored_lookup = self.parent_lookup_kwargs[parent_lookup_kwarg]

            # split each lookup by their __, e.g. "parent__pk" will be split into "parent" and "pk", or
            # "parent__super__pk" would be split into "parent", "super" and "pk"
            lookups = underscored_lookup.split("__")

            try:
                # use the Django ORM to lookup this value, e.g., obj.parent.pk
                lookup_value = reduce(getattr, [obj] + lookups)  # type: ignore[operator,arg-type]
            except AttributeError:
                # Not nested. Act like a standard HyperlinkedRelatedField
                return super().get_url(obj, view_name, request, format)

            # store the lookup_name and value in kwargs, which is later passed to the reverse method
            kwargs.update({parent_lookup_kwarg: lookup_value})

        url = obj.url_prefix + "-" + view_name
        return self.reverse(kwargs=kwargs, request=request, format=format, viewname=url)


class ThemeListSerializerv3(Serializer):
    name = CharField()
    link = PrefixedHyperlinkedIdentityField(
        read_only=True,
        view_name="theme-detail-v3",
        lookup_field="theme",
    )


class ThemeDetailSerializerv3(Serializer):
    sub_themes = PrefixedHyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-list-v3",
        lookup_field="theme",
    )


class SubThemeListSerializerv3(Serializer):
    name = CharField()
    link = NestedPrefixedHyperlinkedIdentityField(
        read_only=True,
        view_name="sub_theme-detail-v3",
        lookup_field="sub_theme",
        parent_lookup_kwargs={"theme": "theme"},
    )


class SubThemeDetailSerializerv3(Serializer):
    topics = NestedPrefixedHyperlinkedIdentityField(
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
    link = NestedPrefixedHyperlinkedIdentityField(
        read_only=True,
        view_name="topic-detail-v3",
        lookup_field="topic",
        parent_lookup_kwargs={
            "theme": "theme",
            "sub_theme": "sub_theme",
        },
    )


class TopicDetailSerializerv3(Serializer):
    geography_types = NestedPrefixedHyperlinkedIdentityField(
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
    link = NestedPrefixedHyperlinkedIdentityField(
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
    geographies = NestedPrefixedHyperlinkedIdentityField(
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
    link = NestedPrefixedHyperlinkedIdentityField(
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
    metrics = NestedPrefixedHyperlinkedIdentityField(
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
    link = NestedPrefixedHyperlinkedIdentityField(
        read_only=True,
        view_name="metric-detail-v3",
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
