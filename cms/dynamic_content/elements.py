import pydantic
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from wagtail import blocks

from cms.dynamic_content import help_texts
from cms.metrics_interface import MetricsAPIInterface
from cms.metrics_interface.field_choices_callables import (
    get_all_age_names,
    get_all_geography_names,
    get_all_geography_type_names,
    get_all_headline_metric_names,
    get_all_sex_names,
    get_all_stratum_names,
    get_all_timeseries_metric_names,
    get_all_topic_names,
    get_all_unique_metric_names,
    get_chart_line_types,
    get_chart_types,
    get_colours,
    get_headline_chart_types,
    get_simplified_chart_types,
)
from validation.data_transfer_models.base import IncomingBaseDataModel

DEFAULT_GEOGRAPHY = "England"
DEFAULT_GEOGRAPHY_TYPE = "Nation"
DEFAULT_SEX = "all"
DEFAULT_AGE = "all"
DEFAULT_STRATUM = "default"
DEFAULT_HEADLINE_CHART_TYPE = "bar"
DEFAULT_SIMPLIFIED_CHART_TYPE = "line_single_simplified"


class BaseMetricsElement(blocks.StructBlock):
    topic = blocks.ChoiceBlock(
        required=True,
        choices=get_all_topic_names,
        help_text=help_texts.TOPIC_FIELD,
    )
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_unique_metric_names,
        help_text=help_texts.METRIC_FIELD,
    )
    geography = blocks.ChoiceBlock(
        required=True,
        choices=get_all_geography_names,
        default=DEFAULT_GEOGRAPHY,
        help_text=help_texts.GEOGRAPHY_FIELD,
    )
    geography_type = blocks.ChoiceBlock(
        required=True,
        choices=get_all_geography_type_names,
        default=DEFAULT_GEOGRAPHY_TYPE,
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
    )
    sex = blocks.ChoiceBlock(
        required=True,
        choices=get_all_sex_names,
        default=DEFAULT_SEX,
        help_text=help_texts.SEX_FIELD,
    )
    age = blocks.ChoiceBlock(
        required=True,
        choices=get_all_age_names,
        default=DEFAULT_AGE,
        help_text=help_texts.AGE_FIELD,
    )
    stratum = blocks.ChoiceBlock(
        required=True,
        choices=get_all_stratum_names,
        default=DEFAULT_STRATUM,
        help_text=help_texts.STRATUM_FIELD,
    )

    def clean(self, value) -> blocks.StructValue:
        """
        Validate the block value, convert it to a StructValue, and return it.

        This method prioritises the basic validation checks defined on the block
        attributes before then completing deeper validation of the values. This ensures
        that, for example, errors raised for missing required attributes are raised
        before deeper, more complex errors.

        Args:
            value: the block value to validate and convert

        Returns:
            a new, validated StructValue object

        Raises:
            StructBlockValidationError if validation errors are found
        """
        # call the super version first to do the basic input validation, then do our
        # deeper validation after
        result = super().clean(value=value)
        self._validate_data_inputs(value=result)
        return result

    @classmethod
    def _validate_data_inputs(cls, *, value: blocks.StructValue) -> None:
        """
        Validates the block value against our metric validations to check the
        combinations of values that have been selected are valid according to our
        logical model.

        This uses the IncomingBaseDataModel which is used for ingestion validation as
        well to ensure consistency. If issues are found, a StrutBlockValidationError is
        raised, otherwise nothing happens and this function will simply return.

        Args:
            value: the block value to validate

        Raises:
            StructBlockValidationError if any problems are found
        """
        # validate and extract these values
        metric_group = cls._validate_metric_group(value=value)
        geography_code = cls._validate_geography_code(value=value)

        try:
            IncomingBaseDataModel(
                **value,
                geography_code=geography_code,
                metric_group=metric_group,
            )
        except pydantic.ValidationError as validation_error:
            # these fields aren't used here but the IncomingBaseDataModel expects them,
            # so we need to ignore errors relating to these fields
            ignore_attrs = {"refresh_date", "parent_theme", "child_theme"}
            block_errors = {
                error["loc"][0]: ValidationError(error["msg"])
                for error in validation_error.errors()
                if error["loc"][0] not in ignore_attrs
            }
            if block_errors:
                raise blocks.StructBlockValidationError(
                    block_errors=block_errors
                ) from validation_error

    @classmethod
    def _validate_metric_group(cls, *, value: blocks.StructValue) -> str:
        """
        Ensures that a metric group is extractable from the block value and returns it.

        Args:
            value: the block value to validate

        Raises:
            StructBlockValidationError on the metric if a group was not extractable
        """
        try:
            return value["metric"].split("_")[1]
        except IndexError as e:
            raise blocks.StructBlockValidationError(
                block_errors={
                    "metric": ValidationError("Invalid metric, could not extract group")
                }
            ) from e

    @classmethod
    def _validate_geography_code(cls, *, value: blocks.StructValue) -> str:
        """
        Ensures that a geography code exists for the selected geography and
        geography_type combination, and returns it.

        This function errors on the geography_type rather than the geography as the user
        selects it after the geography in the UI. We present the error to the user as a
        problem with the geography type not matching the geography rather than the other
        way around and don't mention the code at all as it is an implementational detail
        they don't have any control over.

        Args:
            value: the block value to validate

        Raises:
            StructBlockValidationError on the geography_type if a code isn't findable
        """
        try:
            return MetricsAPIInterface().get_geography_code_for_geography(
                geography=value["geography"], geography_type=value["geography_type"]
            )
        except ObjectDoesNotExist as e:
            raise blocks.StructBlockValidationError(
                block_errors={
                    "geography_type": ValidationError(
                        "Geography type does not match geography"
                    )
                }
            ) from e


class ChartPlotElement(BaseMetricsElement):
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_timeseries_metric_names,
        help_text=help_texts.METRIC_FIELD,
    )
    chart_type = blocks.ChoiceBlock(
        required=True,
        choices=get_chart_types,
        help_text=help_texts.CHART_TYPE_FIELD,
    )
    date_from = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_TO_FIELD,
    )
    label = blocks.TextBlock(
        required=False,
        help_text=help_texts.LABEL_FIELD,
    )
    line_colour = blocks.ChoiceBlock(
        required=True,
        choices=get_colours,
        default=get_colours()[0],
        help_text=help_texts.LINE_COLOUR_FIELD,
    )
    line_type = blocks.ChoiceBlock(
        required=False,
        choices=get_chart_line_types,
        help_text=help_texts.LINE_TYPE_FIELD,
    )
    use_markers = blocks.BooleanBlock(
        default=False,
        required=False,
        help_text=help_texts.USE_MARKERS,
    )
    use_smooth_lines = blocks.BooleanBlock(
        default=True,
        required=False,
        help_text=help_texts.USE_SMOOTH_LINES,
    )

    class Meta:
        icon = "chart_plot"


class HeadlineChartPlotElement(BaseMetricsElement):
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_headline_metric_names,
        help_text=help_texts.METRIC_FIELD,
    )
    chart_type = blocks.ChoiceBlock(
        required=True,
        choices=get_headline_chart_types,
        help_text=help_texts.CHART_TYPE_FIELD,
        default=DEFAULT_HEADLINE_CHART_TYPE,
    )
    line_colour = blocks.ChoiceBlock(
        required=True,
        choices=get_colours,
        default=get_colours()[0],
        help_text=help_texts.LINE_COLOUR_FIELD,
    )
    label = blocks.TextBlock(
        required=False,
        help_text=help_texts.LABEL_FIELD,
    )

    class Meta:
        icon = "chart_plot"


class SimplifiedChartPlotElement(BaseMetricsElement):
    metric = blocks.ChoiceBlock(
        required=True,
        choices=get_all_timeseries_metric_names,
        help_text=help_texts.METRIC_FIELD,
    )
    chart_type = blocks.ChoiceBlock(
        required=True,
        choices=get_simplified_chart_types,
        default=DEFAULT_SIMPLIFIED_CHART_TYPE,
    )
    date_from = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = blocks.DateBlock(
        required=False,
        help_text=help_texts.DATE_TO_FIELD,
    )
    use_smooth_lines = blocks.BooleanBlock(
        default=False,
        required=False,
        help_text=help_texts.USE_SMOOTH_LINES,
    )
