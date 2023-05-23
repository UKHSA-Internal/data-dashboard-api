from django.db.models import Manager
from django.db.utils import ProgrammingError
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import Metric, Topic
from metrics.domain.models import TablePlots


class TablePlotSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.TOPIC_FIELD,
    )
    metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.METRIC_FIELD,
    )
    stratum = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.STRATUM_FIELD,
    )
    geography = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.GEOGRAPHY_FIELD,
    )
    geography_type = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
    )
    date_from = serializers.DateField(
        required=False,
        allow_null=True,
        default="",
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = serializers.DateField(
        required=False,
        allow_null=True,
        default="",
        help_text=help_texts.DATE_FROM_FIELD,
    )
    label = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.LABEL_FIELD,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.populate_choices()
        except (RuntimeError, ProgrammingError):
            pass
        # This is needed because the serializers are loaded by django at runtime
        # Because this is a child serializer, an `instance` must be passed
        # to the parent serializer.
        # Otherwise, we'd have to decorate all our unit tests with access to the db.

    def populate_choices(self):
        self.fields["topic"].choices = self.topic_manager.get_all_names()
        self.fields["metric"].choices = self.metric_manager.get_all_names()

    @property
    def topic_manager(self) -> Manager:
        return self.context.get("topic_manager", Topic.objects)

    @property
    def metric_manager(self) -> Manager:
        return self.context.get("metric_manager", Metric.objects)


class TablePlotsListSerializer(serializers.ListSerializer):
    child = TablePlotSerializer()


class TablesSerializer(serializers.Serializer):
    plots = TablePlotsListSerializer()

    def to_models(self) -> TablePlots:
        return TablePlots(
            plots=self.data["plots"],
        )


class TablesResponseSerializer(serializers.Serializer):
    chart = serializers.FileField(help_text=help_texts.TABLES_RESPONSE_HELP_TEXT)
