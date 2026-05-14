from metrics.domain.models.charts.segments import SegmentParameters
from dataclasses import dataclass

from django.db.models import Manager
from pydantic import BaseModel, model_validator

from metrics.data.models.core_models import CoreTimeSeries, Topic
from metrics.domain.models import DualCategoryChartRequestParams
from metrics.utils.type_hints import CORE_MODEL_MANAGER_TYPE

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_TOPIC_MANAGER = Topic.objects


# =========================================================
# 📦 DATA LAYER (PURE MATRIX ONLY)
# =========================================================


class DualCategoryPlots(BaseModel):
    """
    Pure data matrix

    This class contains NO metadata and NO rendering logic.
    It only guarantees matrix integrity.
    """

    primary_labels: list[str]
    secondary_labels: list[str]
    plots: list[list[float]]

    @model_validator(mode="after")
    def validate_shape(self):
        """
        Ensures matrix consistency:

        - Number of rows must match primary_labels
        - Each row must match secondary_labels
        """

        if len(self.plots) != len(self.primary_labels):
            error_message = "plots row count must match primary_labels length"
            raise ValueError(error_message)

        expected_cols = len(self.secondary_labels)

        for i, row in enumerate(self.plots):
            if len(row) != expected_cols:
                error_message = (
                    f"Row {i} has length {len(row)} but expected {expected_cols}"
                )
                raise ValueError(error_message)

        return self


@dataclass
class DualCategoryPlotsInterface:
    def __init__(
        self,
        *,
        chart_request_params: DualCategoryChartRequestParams,
        core_model_manager: CORE_MODEL_MANAGER_TYPE = DEFAULT_CORE_TIME_SERIES_MANAGER,
        topic_model_manager: Manager = DEFAULT_TOPIC_MANAGER,
    ):
        self.chart_request_params = chart_request_params
        self.core_model_manager = core_model_manager
        self.topic_model_manager = topic_model_manager

    def build_plot_data_from_parameters(self, *, segment_parameters: list[SegmentParameters]):
        return None

    def build_plots_data(self, *, segment_parameters: list[SegmentParameters]):
        self.build_plot_data_from_parameters(segment_parameters=segment_parameters)
        return None
