import contextlib
import datetime
import factory
from metrics.api.models.api_permissions import ApiPermission

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
from django.utils import timezone


class ApiPermissionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ApiPermission

    @classmethod
    def create_record(
        cls,
        name: str = "permission1",
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
        topic_name: str = "COVID-19",
        metric_name: str = "COVID-19_headline_positivity_latest",
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        stratum_name: str = "default",
        age_name: str = "all",
        **kwargs,
    ):
        sub_theme = None
        topic = None
        metric = None
        geography_type = None
        geography = None
        age = None
        stratum = None

        theme, _ = Theme.objects.get_or_create(name=theme_name)
        if sub_theme_name:
            try:
                sub_theme, _ = SubTheme.objects.get_or_create(
                    name=sub_theme_name, theme_id=theme.id
                )
            except:
                pass

        if topic_name:
            topic, _ = Topic.objects.get_or_create(
                name=topic_name, sub_theme_id=sub_theme.id
            )

        if metric_name:
            metric, _ = Metric.objects.get_or_create(
                name=metric_name, topic_id=topic.id
            )

        if geography_type_name:
            geography_type, _ = GeographyType.objects.get_or_create(
                name=geography_type_name
            )

        if geography_name:
            try:
                geography, _ = Geography.objects.get_or_create(
                    name=geography_name,
                    geography_code="E92000001",
                    geography_type_id=geography_type.id,
                )
            except:
                pass

        if age_name:
            age, _ = Age.objects.get_or_create(name=age_name)

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

    @classmethod
    def _make_datetime_timezone_aware(
        cls, datetime_obj: str | datetime.datetime | None
    ) -> datetime.datetime:

        if datetime_obj is None:
            return datetime_obj

        with contextlib.suppress(TypeError):
            # If it is already a datetime object then suppress the resulting TypeError
            datetime_obj = datetime.datetime.strptime(datetime_obj, "%Y-%m-%d")

        try:
            return timezone.make_aware(value=datetime_obj)
        except ValueError:
            # The object is already timezone aware
            return datetime_obj
