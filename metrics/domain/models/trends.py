from metrics.domain.models.headline import HeadlineParameters


class TrendsParameters(HeadlineParameters):
    percentage_metric: str

    @property
    def percentage_metric_name(self) -> str:
        return self.percentage_metric
