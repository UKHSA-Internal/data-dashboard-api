import contextlib

from django.db.models import Manager
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import (
    Age,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["topic"].choices = self.topic_manager.get_all_names()
        self.fields["metric"].choices = self.metric_manager.get_all_names()

    @property
    def topic_manager(self) -> Manager:
        return self.context.get("topic_manager", Topic.objects)

    @property
    def metric_manager(self) -> Manager:
        return self.context.get("metric_manager", Metric.objects)


class HeadlinesQuerySerializerBeta(serializers.Serializer):
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
        self.fields[
            "geography_type"
        ].choices = self.geography_type_manager.get_all_names()
        self.fields["stratum"].choices = self.stratum_manager.get_all_names()
        self.fields["age"].choices = self.age_manager.get_all_names()

    def to_models(self) -> HeadlineParameters:
        return HeadlineParameters(**self.validated_data)

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
