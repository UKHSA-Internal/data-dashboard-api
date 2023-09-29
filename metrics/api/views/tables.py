from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.serializers.tables import (
    TablesResponseSerializer,
    TablesResponseSerializerV3,
    TablesSerializer,
)
from metrics.interfaces.plots import validation
from metrics.interfaces.tables import access

TABLES_API_TAG = "tables"


class TablesView(APIView):
    permission_classes = []

    @extend_schema(
        request=TablesSerializer,
        responses={HTTPStatus.OK.value: TablesResponseSerializer},
        tags=[TABLES_API_TAG],
        deprecated=True,
    )
    @cache_response()
    def post(self, request, *args, **kwargs):
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

        """
        request_serializer = TablesSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        plots_collection = request_serializer.to_models()

        try:
            tabular_data_response: list[dict[str, str]] = access.generate_table(
                plots_collection=plots_collection
            )

        except validation.MetricDoesNotSupportTopicError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data_response)


class TablesViewV3(APIView):
    permission_classes = []

    @extend_schema(
        request=TablesSerializer,
        responses={HTTPStatus.OK.value: TablesResponseSerializerV3},
        tags=[TABLES_API_TAG],
        deprecated=True,
    )
    @cache_response()
    def post(self, request, *args, **kwargs):
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

        """
        request_serializer = TablesSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        plots_collection = request_serializer.to_models()

        try:
            tabular_data: list[dict[str, str]] = access.generate_table_v3(
                plots_collection=plots_collection
            )

        except validation.MetricDoesNotSupportTopicError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data)


class TablesViewV4(APIView):
    permission_classes = []

    @extend_schema(
        request=TablesSerializer,
        responses={HTTPStatus.OK.value: TablesResponseSerializerV3},
        tags=[TABLES_API_TAG],
    )
    @cache_response()
    def post(self, request, *args, **kwargs):
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

        """
        request_serializer = TablesSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        plots_collection = request_serializer.to_models()

        try:
            tabular_data: list[dict[str, str]] = access.generate_table_v4(
                plots_collection=plots_collection
            )

        except validation.MetricDoesNotSupportTopicError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data)
