from django.db.models import Manager
from django.db.utils import ProgrammingError
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import Metric, Topic
from metrics.domain.models import TablePlots


class TablePlotSerializer(serializers.Serializer):
    # Required fields
    topic = serializers.ChoiceField(
        help_text=help_texts.TOPIC_FIELD,
        choices=[],
        required=True,
    )
    metric = serializers.ChoiceField(
        help_text=help_texts.METRIC_FIELD,
        choices=[],
        required=True,
    )
    # Optional fields
    stratum = serializers.CharField(
        help_text=help_texts.STRATUM_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
    geography = serializers.CharField(
        help_text=help_texts.GEOGRAPHY_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
    geography_type = serializers.CharField(
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
    date_from = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        allow_null=True,
        default="",
    )
    date_to = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        allow_null=True,
        default="",
    )
    label = serializers.CharField(
        help_text=help_texts.LABEL_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
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
