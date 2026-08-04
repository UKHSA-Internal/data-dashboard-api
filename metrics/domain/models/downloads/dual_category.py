from metrics.domain.models.plots import ChartRequestParams


class DualCategoryDownloadRequestParams(ChartRequestParams):
    """
    Download request params for dual-category exports.
    """

    secondary_category: str
    segment_secondary_values: list[str]
    primary_field_values: list[str] = []
