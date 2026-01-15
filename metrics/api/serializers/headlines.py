import contextlib
from datetime import datetime

from django.db.models import Manager
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    Geography,
    GeographyType,
    Metric,
    Stratum,
    Topic,
)
from metrics.domain.models.headline import HeadlineParameters


class HeadlinesQuerySerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.TOPIC_FIELD,
    )
    metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.METRIC_FIELD.format(
            "COVID-19_headline_ONSdeaths_7DayChange"
        ),
    )
    geography = serializers.ChoiceField(
        choices=[],
        required=False,
        help_text=help_texts.GEOGRAPHY_FIELD,
    )
    geography_type = serializers.ChoiceField(
        choices=[],
        required=False,
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
    )
    stratum = serializers.ChoiceField(
        choices=[],
        required=False,
        help_text=help_texts.STRATUM_FIELD,
    )
    age = serializers.ChoiceField(
        choices=[],
        required=False,
        help_text=help_texts.AGE_FIELD,
    )
    sex = serializers.ChoiceField(
        choices=["all", "m", "f"],
        required=False,
        help_text=help_texts.SEX_FIELD,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with contextlib.suppress(RuntimeError, ProgrammingError, OperationalError):
            self.populate_choices()

    def populate_choices(self):
        self.fields["topic"].choices = self.topic_manager.get_all_names()
        self.fields["metric"].choices = self.metric_manager.get_all_headline_names()
        self.fields["geography"].choices = self.geography_manager.get_all_names()
        self.fields["geography_type"].choices = (
            self.geography_type_manager.get_all_names()
        )
        self.fields["stratum"].choices = self.stratum_manager.get_all_names()
        self.fields["age"].choices = self.age_manager.get_all_names()

    def to_models(self, request: Request) -> HeadlineParameters:
        return HeadlineParameters(**self.validated_data, request=request)

    @property
    def topic_manager(self) -> Manager:
        return self.context.get("topic_manager", Topic.objects)

    @property
    def metric_manager(self) -> Manager:
        return self.context.get("metric_manager", Metric.objects)

    @property
    def geography_manager(self) -> Manager:
        return self.context.get("geography_manager", Geography.objects)

    @property
    def geography_type_manager(self) -> Manager:
        return self.context.get("geography_type_manager", GeographyType.objects)

    @property
    def stratum_manager(self) -> Manager:
        return self.context.get("stratum_manager", Stratum.objects)

    @property
    def age_manager(self) -> Manager:
        return self.context.get("age_manager", Age.objects)


class HeadlinesResponseSerializer(serializers.Serializer):
    value = serializers.FloatField(help_text=help_texts.HEADLINE_METRIC_VALUE_FIELD)


class CoreHeadlineSerializer(serializers.ModelSerializer):
    """This serializer returns a set of serialized fields from the `CoreTimeSeries` and related models.

    The `DownloadsInterface`, processes download data. This processing includes both merging and casting
    multiple querysets resulting in related fields (through forgein key relations) to be included
    using double underscore syntax.

    Eg: `metric  -> topic -> sub_theme -> theme` becomes `obj.metric__topic__sub_theme_theme__name`

    The `SerializerMethodField()` and `get_<field_name>()` methods enables us to map these to the correct
    field names for the serialized payload.

    Eg: `obj.metric__topic__sub_theme__theme__name` becomes theme
    """

    theme = serializers.SerializerMethodField()
    sub_theme = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    geography_type = serializers.SerializerMethodField()
    geography = serializers.SerializerMethodField()
    metric = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    stratum = serializers.SerializerMethodField()
    period_start = serializers.SerializerMethodField()
    period_end = serializers.SerializerMethodField()

    class Meta:
        """
        The final four fields (sex, period_start, period_end, metric_value)
        belong to the `CoreHeadline` model and can be pulled directly from there
        without the use of `SerializerMethodField()`.
        """

        model = CoreHeadline
        fields = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "age",
            "stratum",
            "sex",
            "period_start",
            "period_end",
            "metric_value",
            "upper_confidence",
            "lower_confidence",
        ]

    @classmethod
    def get_theme(cls, obj) -> str:
        try:
            return obj.metric__topic__sub_theme__theme__name
        except AttributeError:
            return obj.metric.topic.sub_theme.theme.name

    def get_fields(self) -> list[str]:
        fields = super().get_fields()
        confidence_intervals = self.context.get("confidence_intervals", False)

        if not confidence_intervals:
            fields.pop("upper_confidence")
            fields.pop("lower_confidence")
        return fields

    @classmethod
    def get_sub_theme(cls, obj) -> str:
        try:
            return obj.metric__topic__sub_theme__name
        except AttributeError:
            return obj.metric.topic.sub_theme.name

    @classmethod
    def get_topic(cls, obj) -> str:
        try:
            return obj.metric__topic__name
        except AttributeError:
            return obj.metric.topic.name

    @classmethod
    def get_geography_type(cls, obj) -> str:
        try:
            return obj.geography__geography_type__name
        except AttributeError:
            return obj.geography.geography_type.name

    @classmethod
    def get_geography(cls, obj) -> str:
        try:
            return obj.geography__name
        except AttributeError:
            return obj.geography.name

    @classmethod
    def get_metric(cls, obj) -> str:
        try:
            return obj.metric__name
        except AttributeError:
            return obj.metric.name

    @classmethod
    def get_age(cls, obj) -> str:
        try:
            return obj.age__name
        except AttributeError:
            return obj.age.name

    @classmethod
    def get_stratum(cls, obj) -> str:
        try:
            return obj.stratum__name
        except AttributeError:
            return obj.stratum.name

    @classmethod
    def get_period_start(cls, obj) -> str:
        return datetime.strftime(obj.period_start, "%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_period_end(cls, obj) -> str:
        return datetime.strftime(obj.period_end, "%Y-%m-%d %H:%M:%S")
