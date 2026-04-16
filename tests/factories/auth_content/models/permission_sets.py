import factory

from auth_content.models.permission_sets import PermissionSet


class PermissionSetFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `PermissionSet` instances for tests
    """

    class Meta:
        model = PermissionSet

    @classmethod
    def create_wildcard_permission_set(cls):
        WILDCARD_VALUE = "-1"

        return cls.create(
            name="Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All) | Geography: * (All)",
            theme=WILDCARD_VALUE,
            sub_theme=WILDCARD_VALUE,
            topic=WILDCARD_VALUE,
            metric=WILDCARD_VALUE,
            geography_type=WILDCARD_VALUE,
            geography=WILDCARD_VALUE
        )

    @classmethod
    def create_permission_set(cls, name, theme, sub_theme, topic, metric, geography_type, geography):

        return cls.create(
            name=name,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography_type=geography_type,
            geography=geography
        )
