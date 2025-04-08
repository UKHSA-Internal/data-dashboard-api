import os
from http import HTTPStatus

from django.http import FileResponse
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

import config
from caching.private_api.decorators import cache_response
from metrics.api.enums import AppMode
from metrics.api.serializers import ChartsSerializer
from metrics.api.serializers.charts import (
    ChartsResponseSerializer,
    EncodedChartResponseSerializer,
    EncodedChartsRequestSerializer,
)
from metrics.domain.models import ChartRequestParams
from metrics.interfaces.charts import access
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)

CHARTS_API_TAG = "charts"


class ChartsView(APIView):
    permission_classes = []

    def get_permissions(self) -> list[type[permissions.BasePermission]]:
        if AppMode.CMS_ADMIN.value == config.APP_MODE:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        request=ChartsSerializer,
        responses={HTTPStatus.OK.value: ChartsResponseSerializer},
        tags=[CHARTS_API_TAG],
        examples=[
            OpenApiExample(
                "COVID-19 example",
                value={
                    "file_format": "png",
                    "chart_height": 300,
                    "chart_width": 900,
                    "x_axis": "date",
                    "y_axis": "metric",
                    "x_axis_title": "",
                    "y_axis_title": "",
                    "y_axis_minimum_value": 0,
                    "y_axis_maximum_value": "",
                    "plots": [
                        {
                            "topic": "COVID-19",
                            "metric": "COVID-19_cases_casesByDay",
                            "stratum": "default",
                            "age": "all",
                            "geography": "England",
                            "geography_type": "Nation",
                            "sex": "all",
                            "date_from": "2022-01-01",
                            "date_to": "2023-02-01",
                            "chart_type": "line_multi_coloured",
                            "label": "",
                            "line_colour": "TREND_LINE_NEUTRAL",
                            "line_type": "SOLID",
                            "use_smooth_lines": "false",
                        }
                    ],
                },
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification.

        Multiple plots can be added as an array of objects from the request body.
        This payload takes the following set of parameters for each chart plot:

        | Parameter name   | Description                                                                | Example                  | Mandatory |
        |------------------|----------------------------------------------------------------------------|--------------------------|-----------|
        | `topic`          | The name of the disease/threat                                             | COVID-19                 | Yes       |
        | `metric`         | The name of the metric being queried for                                   | COVID-19_deaths_ONSByDay | Yes       |
        | `chart_type`     | The type of chart to use for the individual plot                           | line_with_shaded_section | Yes       |
        | `stratum`        | The smallest subgroup a metric can be broken down into                     | default                  | No        |
        | `geography`      | The geography constraints to apply any data filtering to                   | London                   | No        |
        | `geography_type` | The type of geographical categorisation to apply any data filtering to     | Nation                   | No        |
        | `sex`            | The gender to filter for, defaults to all                                  | F                        | No        |
        | `age`            | The patient age band                                                       | 0_4                      | No        |
        | `date_from`      | The date from which to start the data slice from. In the format YYYY-MM-DD | 2023-01-01               | No        |
        | `date_to`        | The date to end the data slice to. In the format YYYY-MM-DD                | 2023-05-01               | No        |
        | `label`          | The label to assign on the legend for this individual plot                 | Females                  | No        |
        | `line_colour`    | The colour to use for the line of this individual plot                     | BLUE                     | No        |
        | `line_type`      | The type to assign for this individual plot i.e. SOLID or DASH             | DASH                     | No        |

        ---

        # Note:

        This endpoint has been superseded on the dashboard by `charts/v3` which returns an `SVG` chart in its response.
        This endpoint has been kept for diagnostics/testing because it returns a `png`, which can be directly
        viewed in swagger.

        ---

        # Main errors

        There are certain combination of `topic / metric / chart_type` which do not make sense.

        This is primarily because a set of `metric` values are not available for every `topic`.

        As well as this, certain `metric` names reference data of a certain profile.

        For example, we would only expect to create line graphs with timeseries data.
        But we don't expect to _headline_ type data to be valid for line graphs.

        ---

        ## Selected metric not available for topic

        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a metric like `COVID-19_deaths_ONSByDay` (which is only used for `COVID-19`)
        is being asked for with a topic of `Influenza`.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `Influenza` does not have a corresponding metric of `COVID-19`

        ---

        ## Dates not in chronological order

        In cases where a date provided to the `date_from` property is a later date than the one provided to the `date_to`
        property an HTTP 400 BAD REQUEST with the following error message:
        Invalid plot parameter provided. Please check the date range and topic provided

        ---

        # Changing the size of the graph

        If you are not happy with the default width and/or height of the graph you can override the values by setting one or both of them:

        `chart_height`

        `chart_width`

        ---

        # Choosing what to display along the x and y axis

        By default, dates will be displayed on the x axis and metric values on the y axis. If you want to
        override either/both of these values then you can do so as follows:

        `x_axis` Example: `x_axis: "stratum"`

        `y_axis` Example: `y_axis: "stratum"`

        ---

        # Choosing what to display as the x and/or y axis titles

        By default, nothing will be displayed on the x axis or y axis titles.
        If you want to override either/both of these values then you can do so as follows:

        `x_axis_title` Example: `x_axis_title: "Dates"`

        `y_axis_title` Example: `y_axis_title: "Number of cases"`

        ---

        # Choosing a y-axis minimum and maximum value (y-axis range)

        By default all charts will start with a y-axis minimum value of 0, this means that a chart's y-axis range starts
        at 0 and ends at the highest value in the data set.

        With the ability to set a manual y-axis minimum and maximum value you can set a custom range for timeseries
        charts. For example if a chart's lowest value is 10,000 it is now possible to set a value between 0 and 10,000
        for the chart's y-axis starting value.

        The is also possible for the maximum value, for example a chart where the highest value is 20,000 can have a
        maximum value of any number above 20,000. This functionality enables charts to be set to the same scale where
        they will be place alongside one another on the dashboard.

        Please not that if a minimum value is provided that is `higher` than the minimum value in the dataset the
        `y_axis_minimum_value` will be ignored and the lowest value from the dataset will be used. This is the same
        for `y_axis_maximum_value` if the value provided is `lower` than the highest value in the dataset
        the highest value from the dataset will be used.

        """
        request_serializer = ChartsSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        chart_request_params: ChartRequestParams = request_serializer.to_models(
            request=request
        )

        try:
            filename: str = access.generate_chart_as_file(
                chart_request_params=chart_request_params,
            )
        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return self._return_image(filename=filename)

    @staticmethod
    def _return_image(*, filename: str) -> FileResponse:
        image = open(filename, "rb")
        response = FileResponse(image)

        os.remove(filename)

        return response


class EncodedChartsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=EncodedChartsRequestSerializer,
        responses={HTTPStatus.OK.value: EncodedChartResponseSerializer},
        tags=[CHARTS_API_TAG],
    )
    @cache_response()
    def post(cls, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification.

        Multiple plots can be added as an array of objects from the request body.
        This payload takes the following set of parameters for each chart plot:

        | Parameter name   | Description                                                                | Example                  | Mandatory |
        |------------------|----------------------------------------------------------------------------|--------------------------|-----------|
        | `topic`          | The name of the disease/threat                                             | COVID-19                 | Yes       |
        | `metric`         | The name of the metric being queried for                                   | COVID-19_deaths_ONSByDay | Yes       |
        | `chart_type`     | The type of chart to use for the individual plot                           | line_with_shaded_section | Yes       |
        | `stratum`        | The smallest subgroup a metric can be broken down into                     | default                  | No        |
        | `geography`      | The geography constraints to apply any data filtering to                   | London                   | No        |
        | `geography_type` | The type of geographical categorisation to apply any data filtering to     | Nation                   | No        |
        | `sex`            | The gender to filter for, defaults to all                                  | F                        | No        |
        | `age`            | The patient age band                                                       | 0_4                      | No        |
        | `date_from`      | The date from which to start the data slice from. In the format YYYY-MM-DD | 2023-01-01               | No        |
        | `date_to`        | The date to end the data slice to. In the format YYYY-MM-DD                | 2023-05-01               | No        |
        | `label`          | The label to assign on the legend for this individual plot                 | Females                  | No        |
        | `line_colour`    | The colour to use for the line of this individual plot                     | BLUE                     | No        |
        | `line_type`      | The type to assign for this individual plot i.e. SOLID or DASH             | DASH                     | No        |

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
        For example, if a timeseries type metric like `COVID-19_deaths_ONSByDay`
        is being asked for with a `waffle` chart.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `COVID-19_deaths_ONSByDay` is not compatible with `waffle` chart types

        ---

        ## Selected metric not available for topic

        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a metric like `COVID-19_deaths_ONSByDay` (which is only used for `COVID-19`)
        is being asked for with a topic of `Influenza`.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `Influenza` does not have a corresponding metric of `COVID-19`
        ---
        # Changing the size of the graph

        If you are not happy with the default width and/or height of the graph you can override
        the values by setting one or both of them:

        `chart_height`

        `chart_width`

        ---

        # Choosing what to display along the x and y axis

        By default, dates will be displayed on the x axis and metric values on the y axis. If you want to
        override either/both of these values then you can do so as follows:

        `x_axis` Example: `x_axis: "stratum"`

        `y_axis` Example: `y_axis: "stratum"`

        ---

        # Choosing what to display as the x and/or y axis titles

        By default, nothing will be displayed on the x axis or y axis titles.
        If you want to override either/both of these values then you can do so as follows:

        `x_axis_title` Example: `x_axis_title: "Dates"`

        `y_axis_title` Example: `y_axis_title: "Number of cases"`

        ---

        # Choosing a y-axis minimum and maximum value (y-axis range)

        By default all charts will start with a y-axis minimum value of 0, this means that a chart's y-axis range starts
        at 0 and ends at the highest value in the data set.

        With the ability to set a manual y-axis minimum and maximum value you can set a custom range for timeseries
        charts. For example if a chart's lowest value is 10,000 it is now possible to set a value between 0 and 10,000
        for the chart's y-axis starting value.

        The is also possible for the maximum value, for example a chart where the highest value is 20,000 can have a
        maximum value of any number above 20,000. This functionality enables charts to be set to the same scale where
        they will be place alongside one another on the dashboard.

        Please not that if a minimum value is provided that is `higher` than the minimum value in the dataset the
        `y_axis_minimum_value` will be ignored and the lowest value from the dataset will be used. This is the same
        for `y_axis_maximum_value` if the value provided is `lower` than the highest value in the dataset
        the highest value from the dataset will be used.

        """
        request_serializer = EncodedChartsRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        chart_request_params = request_serializer.to_models(request=request)

        try:
            response: dict[str, str] = access.generate_encoded_chart(
                chart_request_params=chart_request_params,
            )

            serializer = EncodedChartResponseSerializer(data=response)
            serializer.is_valid(raise_exception=True)

        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(data=serializer.data)
