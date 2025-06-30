from metrics.domain.models.headline import HeadlineParameters


class TrendsParameters(HeadlineParameters):
    percentage_metric: str

    @property
    def percentage_metric_name(self) -> str:
        return self.percentage_metric

    def to_dict_for_main_metric_query(self):
        return super().to_dict_for_query()

    def to_dict_for_percentage_metric_query(self):
        params = super().to_dict_for_query()
        params["metric"] = self.percentage_metric
        return params
