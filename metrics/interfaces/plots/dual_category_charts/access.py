class DualCategoryPlotsInterface:
    def __init__(
        self,
        *,
        chart_request_parameters,
        core_model_manager,
        topic_model_manager,
    ):
        self.chart_request_parameters = chart_request_parameters
        self.core_model_manager = core_model_manager
        self.topic_model_manager = topic_model_manager