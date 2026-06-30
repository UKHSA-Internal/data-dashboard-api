from metrics.domain.models.plots import ChartRequestParams


class DualCategoryTableRequestParams(ChartRequestParams):
    secondary_category: str
    segment_secondary_values: list[str]
    primary_field_values: list[str] = []
