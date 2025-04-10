import factory
from metrics.data.models.rbac_models import RBACPermission

from metrics.data.models.core_models import (
    Age,
    Geography,
    GeographyType,
    Metric,
    Stratum,
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
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
        topic_name: str | None = None,
        metric_name: str | None = None,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        age_name: str | None = None,
        **kwargs,
    ):
        theme, _ = Theme.objects.get_or_create(name=theme_name)

        sub_theme = SubTheme.objects.filter(name=sub_theme_name, theme=theme).first()
        if not sub_theme and sub_theme_name:
            sub_theme, _ = SubTheme.objects.get_or_create(
                name=sub_theme_name, theme=theme
            )

        topic = None
        if topic_name:
            topic = Topic.objects.filter(name=topic_name, sub_theme=sub_theme).first()
            if not topic and topic_name:
                topic, _ = Topic.objects.get_or_create(
                    name=topic_name, sub_theme=sub_theme
                )

        metric = None
        if metric_name:
            metric = Metric.objects.filter(name=metric_name, topic=topic).first()
            if not metric and metric_name:
                metric, _ = Metric.objects.get_or_create(name=metric_name, topic=topic)

        geography_type = None
        if geography_type_name:
            geography_type, _ = GeographyType.objects.get_or_create(
                name=geography_type_name
            )

        geography = None
        if geography_name:
            geography = Geography.objects.filter(
                name=geography_name, geography_type=geography_type
            ).first()
            if not geography and geography_name:
                geography, _ = Geography.objects.get_or_create(
                    name=geography_name,
                    geography_code="E92000001",
                    geography_type=geography_type,
                )

        age = None
        if age_name:
            age, _ = Age.objects.get_or_create(name=age_name)

        stratum = None
        if stratum_name:
            stratum, _ = Stratum.objects.get_or_create(name=stratum_name)

        return cls.create(
            name=name,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography_type=geography_type,
            geography=geography,
            stratum=stratum,
            age=age,
            **kwargs,
        )
