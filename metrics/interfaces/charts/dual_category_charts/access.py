from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
)


def generate_chart_as_file(
    *, chart_request_params: DualCategoryChartRequestParams
) -> bytes:
    raise NotImplementedError


def generate_encoded_chart(
    *, chart_request_params: DualCategoryChartRequestParams
) -> dict[str, str]:
    raise NotImplementedError
