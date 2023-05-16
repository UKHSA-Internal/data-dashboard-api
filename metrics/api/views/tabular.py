from http import HTTPStatus
from typing import Dict, List

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers.charts import ChartsSerializer
from metrics.api.serializers.tabular import TabularResponseSerializer, TabularSerializer
from metrics.data.access.core_models import (
    get_month_end_timeseries_metric_values_from_date,
)
from metrics.interfaces.charts.validation import ChartTypeDoesNotSupportMetricError
from metrics.interfaces.tabular import access


class OldTabularView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(deprecated=True)
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


class TabularView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        request=TabularSerializer,
        responses={HTTPStatus.OK.value: TabularResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        """This endpoint can be used to generate chart data in tabular format

        Multiple plots can be added as an array of objects from the request body.
        This payload takes the following set of parameters for each chart plot:

        | Parameter name   | Description                                                                | Example                  | Mandatory |
        |------------------|----------------------------------------------------------------------------|--------------------------|-----------|
        | `topic`          | The name of the disease/threat                                             | COVID-19                 | Yes       |
        | `metric`         | The name of the metric being queried for                                   | new_cases_daily          | Yes       |
        | `chart_type`     | The type of chart to use for the individual plot                           | line_with_shaded_section | Yes       |
        | `stratum`        | The smallest subgroup a metric can be broken down into                     | 0_4                      | No        |
        | `geography`      | The geography constraints to apply any data filtering to                   | London                   | No        |
        | `geography_type` | The type of geographical categorisation to apply any data filtering to     | Nation                   | No        |
        | `date_from`      | The date from which to start the data slice from. In the format YYYY-MM-DD | 2023-01-01               | No        |
        | `date_to`        | The date to end the data slice to. In the format YYYY-MM-DD                | 2023-05-01               | No        |
        | `label`          | The label to assign on the legend for this individual plot                 | 15 to 44 years old       | No        |

        ---

        # Main errors

        There are certain combination of `topic / metric / chart_type` which do not make sense.

        This is primarily because a set of `metric` values are not available for every `topic`.

        As well as this, certain `metric` names reference data of a certain profile.

        For example, we would only expect to create line graphs with timeseries data.
        But we don't expect to _headline_ type data to be valid for line graphs.

        ---

        ## Incompatible timeseries type metrics with waffle charts

        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a timeseries type metric like `new_cases_daily` is being asked for with a `waffle` chart.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `new_cases_daily` is not compatible with `waffle` chart types

        ---

        ## Selected metric not available for topic

        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a metric like `new_cases_daily` (which is only used for `COVID-19`) is being asked for with a topic of `Influenza`.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `Influenza` does not have a corresponding metric of `COVID-19`
        """
        request_serializer = ChartsSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        chart_plot_models = request_serializer.to_models()

        try:
            tabular_data_response: str = access.generate_tabular_output(
                chart_plots=chart_plot_models,
            )
        except ChartTypeDoesNotSupportMetricError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data_response)
