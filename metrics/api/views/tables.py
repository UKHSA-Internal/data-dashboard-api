import logging
from http import HTTPStatus

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.api.serializers.tables import TablesResponseSerializer, TablesSerializer
from metrics.api.views.charts.subplot_charts.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)
from metrics.interfaces.tables import access

TABLES_API_TAG = "tables"

logger = logging.getLogger(__name__)


class TablesView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=TablesSerializer,
        responses={HTTPStatus.OK.value: TablesResponseSerializer},
        tags=[TABLES_API_TAG],
    )
    @cache_response()
    @require_authorisation
    def post(cls, request, *args, **kwargs):
        """This endpoint can be used to generate chart data in tabular format.

        Multiple plots can be added as an array of objects from the request body.

        This payload takes the following set of parameters for each plot:

        | Parameter name   | Description                                                                | Example                  | Mandatory |
        |------------------|----------------------------------------------------------------------------|--------------------------|-----------|
        | `topic`          | The name of the disease/threat                                             | COVID-19                 | Yes       |
        | `metric`         | The name of the metric being queried for                                   | COVID-19_deaths_ONSByDay | Yes       |
        | `stratum`        | The smallest subgroup a metric can be broken down into                     | default                  | No        |
        | `geography`      | The geography constraints to apply any data filtering to                   | London                   | No        |
        | `geography_type` | The type of geographical categorisation to apply any data filtering to     | Nation                   | No        |
        | `age`            | The patient age band                                                       | 0_4                      | No        |
        | `date_from`      | The date from which to start the data slice from. In the format YYYY-MM-DD | 2023-01-01               | No        |
        | `date_to`        | The date to end the data slice to. In the format YYYY-MM-DD                | 2023-05-01               | No        |
        | `label`          | The label to assign on the legend for this individual plot                 | Daily Covid deaths       | No        |

        ---

        # Main errors
        There are certain combination of `topic / metric` which do not make sense.
        This is primarily because a set of `metric` values are not available for every `topic`.
        As well as this, certain `metric` names reference data of a certain profile.

        ---

        ## Selected metric not available for topic

        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a metric like `COVID-19_deaths_ONSByDay` (which is only used for `COVID-19`)
        is being asked for with a topic of `Influenza`.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `Influenza` does not have a corresponding metric of `COVID-19`

        ---

        ## Ordering of data

        Note that for tables which are `date` based i.e. where the `x_axis` field is set to `date`.

        Then the data will be returned in descending order from newest -> oldest:

        ```
        | 2023-09-29 | 1 |
        | 2023-09-28 | 2 |
        | 2023-09-27 | 3 |
        ```

        For tables which **not** `date` based i.e. where the `x_axis` field is set to something like `age`.

        Then the data will be returned in ascending order:

        ```
        | 00 - 04 | 1 |
        | 05 - 09 | 2 |
        | 10 - 14 | 3 |
        ```

        """
        request_serializer = TablesSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        request_params = request_serializer.to_models(request=request)

        try:
            tabular_data: list[dict[str, str]] = access.generate_table_for_full_plots(
                request_params=request_params
            )
        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data)


class TablesSubplotView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=SubplotChartRequestSerializer,
        examples=[
            OpenApiExample(
                name="MMR1 (2 years)", value=REQUEST_PAYLOAD_EXAMPLE, request_only=True
            )
        ],
        tags=[TABLES_API_TAG],
    )
    @cache_response()
    @require_authorisation
    def post(cls, request, *args, **kwargs):
        serializer = SubplotChartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subplot_chart_parameters: SubplotChartRequestParameters = serializer.to_models(
            request=request
        )

        logger.info(
            "Subplot chart parameters: %s", subplot_chart_parameters.model_dump()
        )
        logger.info("This endpoint is incomplete, returning fake data")

        tabular_data = [
            {
                "reference": "England",
                "values": [
                    {
                        "label": "6-in-1 (12 months)",
                        "value": "87.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Rota (12 months)",
                        "value": "85.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB (12 months)",
                        "value": "82.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "6-in-1 (24 months)",
                        "value": "84.0000",
                        "in_reporting_delay_period": True,
                    },
                    {
                        "label": "PCV booster (24 months)",
                        "value": "88.0000",
                        "in_reporting_delay_period": True,
                    },
                    {
                        "label": "MMR1 (24 months)",
                        "value": "86.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Hib/MenC (24 months)",
                        "value": "89.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB booster (24 months)",
                        "value": "85.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "5-in-1 (5 years)",
                        "value": "83.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "4-in-1 (5 years)",
                        "value": "90.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "East Midlands",
                "values": [
                    {
                        "label": "6-in-1 (12 months)",
                        "value": "89.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Rota (12 months)",
                        "value": "88.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB (12 months)",
                        "value": "85.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "6-in-1 (24 months)",
                        "value": "87.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "PCV booster (24 months)",
                        "value": "90.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MMR1 (24 months)",
                        "value": "89.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Hib/MenC (24 months)",
                        "value": "91.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB booster (24 months)",
                        "value": "88.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "5-in-1 (5 years)",
                        "value": "86.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "4-in-1 (5 years)",
                        "value": "92.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "Nottingham",
                "values": [
                    {
                        "label": "6-in-1 (12 months)",
                        "value": "72.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Rota (12 months)",
                        "value": "69.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB (12 months)",
                        "value": "67.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "6-in-1 (24 months)",
                        "value": "68.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "PCV booster (24 months)",
                        "value": "73.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MMR1 (24 months)",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Hib/MenC (24 months)",
                        "value": "74.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB booster (24 months)",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "5-in-1 (5 years)",
                        "value": "66.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "4-in-1 (5 years)",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]

        return Response(tabular_data)
