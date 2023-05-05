from typing import Dict, List

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.data.access.core_models import (
    get_month_end_timeseries_metric_values_from_date,
)


class TabularView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, *args, **kwargs):
        """This endpoint can be used to generate a summary of the chart data but in tabular format
        There are 2 mandatory URL parameters:

        - `topic` - relates to a type of disease (eg COVID-19, Influenza)

        - `metric` - refers to the type of metric (eg, new_cases_daily, cases_age_sex)

        """
        topic: str = kwargs["topic"]
        metric_name: str = kwargs["metric"]

        result: List[Dict[str, str]] = get_month_end_timeseries_metric_values_from_date(
            metric_name=metric_name, topic=topic
        )

        return Response(result)
