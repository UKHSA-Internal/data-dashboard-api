from http import HTTPStatus
from typing import Dict, List

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers.tables import TablesResponseSerializer, TablesSerializer
from metrics.data.access.core_models import (
    get_month_end_timeseries_metric_values_from_date,
)
from metrics.domain.models import PlotParameters
from metrics.interfaces.charts import access, validation
from metrics.interfaces.tables import access


class OldTabularView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, *args, **kwargs):
        """This endpoint can be used to generate a summary of the chart data but in tabular format
        There are 2 mandatory URL parameters:

        - `topic` - relates to a type of disease (eg COVID-19, Influenza)

        - `metric` - refers to the type of metric (eg, new_cases_daily, cases_age_sex)

        """
        plot_parameters = PlotParameters(
            topic=kwargs["topic"],
            metric=kwargs["metric"],
            chart_type="tabular",
        )

        result: List[Dict[str, str]] = get_month_end_timeseries_metric_values_from_date(
            plot_parameters=plot_parameters,
        )

        return Response(result)


class TablesView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        request=TablesSerializer,
        responses={HTTPStatus.OK.value: TablesResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        """This endpoint can be used to generate chart data in tabular format.

        Multiple plots can be added as an array of objects from the request body.

        This payload takes the following set of parameters for each plot:

        | Parameter name   | Description                                                                | Example                  | Mandatory |
        |------------------|----------------------------------------------------------------------------|--------------------------|-----------|
        | `topic`          | The name of the disease/threat                                             | COVID-19                 | Yes       |
        | `metric`         | The name of the metric being queried for                                   | new_cases_daily          | Yes       |
        | `stratum`        | The smallest subgroup a metric can be broken down into                     | 0_4                      | No        |
        | `geography`      | The geography constraints to apply any data filtering to                   | London                   | No        |
        | `geography_type` | The type of geographical categorisation to apply any data filtering to     | Nation                   | No        |
        | `date_from`      | The date from which to start the data slice from. In the format YYYY-MM-DD | 2023-01-01               | No        |
        | `date_to`        | The date to end the data slice to. In the format YYYY-MM-DD                | 2023-05-01               | No        |
        | `label`          | The label to assign on the legend for this individual plot                 | 15 to 44 years old       | No        |

        ---

        # Main errors
        There are certain combination of `topic / metric` which do not make sense.
        This is primarily because a set of `metric` values are not available for every `topic`.
        As well as this, certain `metric` names reference data of a certain profile.

        ---

        ## Selected metric not available for topic
        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a metric like `new_cases_daily` (which is only used for `COVID-19`) is being asked for with a topic of `Influenza`.
        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `Influenza` does not have a corresponding metric of `COVID-19`

        """
        request_serializer = TablesSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        table_plot_models = request_serializer.to_models()

        try:
            tabular_data_response: List[Dict[str, str]] = access.generate_table(
                chart_plots=table_plot_models
            )

        except validation.MetricDoesNotSupportTopicError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data_response)
