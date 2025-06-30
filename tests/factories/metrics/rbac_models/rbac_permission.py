import factory
from metrics.data.models.rbac_models import RBACPermission

from metrics.data.models.core_models import (
    Geography,
    GeographyType,
    Metric,
    SubTheme,
    Theme,
    Topic,
)


class RBACPermissionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = RBACPermission

    @classmethod
    def create_record(
        cls,
        name: str = "all_infectious_respiratory_data",
        theme: str = "infectious_disease",
        sub_theme: str = "respiratory",
        topic: str | None = None,
        metric: str | None = None,
        geography: str | None = None,
        geography_type: str | None = None,
        geography_code: str = "E92000001",
        **kwargs,
    ):
        theme, _ = Theme.objects.get_or_create(name=theme)

        if sub_theme:
            sub_theme, _ = SubTheme.objects.get_or_create(name=sub_theme, theme=theme)

        if topic:
            topic, _ = Topic.objects.get_or_create(name=topic, sub_theme=sub_theme)

        if metric:
            metric, _ = Metric.objects.get_or_create(name=metric, topic=topic)

        if geography_type:
            geography_type, _ = GeographyType.objects.get_or_create(name=geography_type)

        if geography:
            geography, _ = Geography.objects.get_or_create(
                name=geography,
                geography_code=geography_code,
                geography_type=geography_type,
            )

        return cls.create(
            name=name,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography_type=geography_type,
            geography=geography,
            **kwargs,
        )
