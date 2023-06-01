import os
from http import HTTPStatus

from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import ChartsSerializer
from metrics.api.serializers.charts import ChartsResponseSerializer
from metrics.interfaces.charts import access, validation

CHARTS_API_TAG = "charts"


class ChartsView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        request=ChartsSerializer,
        responses={HTTPStatus.OK.value: ChartsResponseSerializer},
        tags=[CHARTS_API_TAG],
    )
    def post(self, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification.

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
        For example, if a timeseries type metric like `new_cases_daily` is being asked for with a `waffle` chart.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `new_cases_daily` is not compatible with `waffle` chart types

        ---

        ## Selected metric not available for topic

        In these cases, this endpoint will return an HTTP 400 BAD REQUEST.
        For example, if a metric like `new_cases_daily` (which is only used for `COVID-19`) is being asked for with a topic of `Influenza`.

        Then an HTTP 400 BAD REQUEST is returned with the following error message:
            `Influenza` does not have a corresponding metric of `COVID-19`
        ---
        # Changing the size of the graph

        If you are not happy with the default width and/or height of the graph you can override the values by setting one or both of them:

        `chart_height`

        `chart_width`
        """
        request_serializer = ChartsSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        chart_plot_models = request_serializer.to_models()

        try:
            filename: str = access.generate_chart(
                chart_plots=chart_plot_models,
            )
        except validation.ChartTypeDoesNotSupportMetricError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return self._return_image(filename=filename)

    @staticmethod
    def _return_image(filename: str) -> FileResponse:
        image = open(filename, "rb")
        response = FileResponse(image)

        os.remove(filename)

        return response
