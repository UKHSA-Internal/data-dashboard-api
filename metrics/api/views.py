import os
from http import HTTPStatus

from django.http import FileResponse, HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import ChartsQuerySerializer, ChartsRequestSerializer
from metrics.api.serializers.stats import HeadlinesQuerySerializer
from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data
from metrics.interfaces.charts import access, data_visualization_superseded, validation
from metrics.interfaces.headlines.access import (
    BaseInvalidHeadlinesRequestError,
    generate_headline_number,
)


class HealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        return HttpResponse(HTTPStatus.OK.value)


DEPRECATION_DATE_CHARTS_ENDPOINT = "Wed, 19 Apr 2023 23:59:59 GMT"
DEPRECATION_MESSAGE_PREDICT_CONFIDENCE = (
    f"This endpoint has been deprecated.\n"
    f"This functionality can now be found within the `/charts/v2/` endpoint.\n"
    f"Deprecation date: {DEPRECATION_DATE_CHARTS_ENDPOINT}"
)

DEPRECATION_HEADERS_PREDICT_CONFIDENCE = {
    "Deprecation": DEPRECATION_DATE_CHARTS_ENDPOINT,
}


class ChartView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(parameters=[ChartsQuerySerializer], deprecated=True)
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification

        There are 2 mandatory URL parameters:

        - `topic` - relates to a type of disease

        - `category` - refers to the type of metric (like deaths or cases)

        Currently, the available permutations are:
        | Topic | Category |
        | ----- | -------- |
        | COVID-19 | Vaccinations |
        | COVID-19 | Cases |
        | COVID-19 | Deaths |
        | Influenza | Healthcare |
        | Influenza | Testing |

        Where a given permutation is not available the endpoint will respond with a `HTTP 404 NOT FOUND` error

        There is also an optional query param of `file_format`.
        By default, this will be set to `svg`.

        """
        category: str = kwargs["category"]
        topic: str = kwargs["topic"]

        query_serializer = ChartsQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        file_format = query_serializer.data["file_format"]

        try:
            filename: str = data_visualization_superseded.generate_corresponding_chart(
                topic=topic, category=category, file_format=file_format
            )
        except data_visualization_superseded.ChartNotSupportedError:
            return Response(
                status=HTTPStatus.NOT_FOUND,
                headers=DEPRECATION_HEADERS_PREDICT_CONFIDENCE,
            )

        return self._return_image(filename=filename)

    @staticmethod
    def _return_image(filename: str) -> FileResponse:
        image = open(filename, "rb")
        response = FileResponse(image, headers=DEPRECATION_HEADERS_PREDICT_CONFIDENCE)

        os.remove(filename)

        return response


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [HasAPIKey]

    @extend_schema(
        operation_id="upload_file",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
        deprecated=True,
    )
    def put(self, request, *args, **kwargs):
        """
        Note that this endpoint is **deprecated** and should only be used for demo/testing purposes.
        """
        load_core_data(filename=request.FILES.get("file"))
        generate_api_time_series()
        return Response(status=204)


class ChartsView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(parameters=[ChartsRequestSerializer])
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification

        Note that the `date_from` param must be in the format `YYYY-MM-DD`.

        E.g. for the 1st of October 2022, the `date_from` value would be `2022-10-01`

        """
        query_serializer = ChartsRequestSerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        topic = query_serializer.data["topic"]
        metric = query_serializer.data["metric"]
        chart_type = query_serializer.data["chart_type"]
        date_from = query_serializer.data.get("date_from")

        try:
            filename: str = access.generate_chart(
                topic=topic, metric=metric, chart_type=chart_type, date_from=date_from
            )
        except data_visualization_superseded.ChartNotSupportedError:
            return Response(status=HTTPStatus.NOT_FOUND)
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


class HeadlinesView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(parameters=[HeadlinesQuerySerializer])
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to retrieve headline-type numbers for a given `metric` & `topic` combination.

        Note that this endpoint will only return single-headline number type data.
        If the `metric` provided relates to timeseries type data then the request will be deemed invalid.

        ---

        For example, a request for the following would be **invalid**:

        - metric =`new_cases_daily`

        - topic = `COVID-19`

        This would be **invalid** because the `metric` of `new_cases_daily` relates to timeseries data,
        which is not represented by a single headline-type figure.

        ---

        Whereas, a request for the following would be **valid**:

        - metric =`new_cases_7days_sum`

        - topic = `COVID-19`

        This would be **valid** because the `metric` of `new_cases_7days_sum` relates to headline data,
        which can be represented by a single headline-type figure.

        """
        query_serializer = HeadlinesQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        topic = query_serializer.data["topic"]
        metric = query_serializer.data["metric"]

        try:
            headline_number: str = generate_headline_number(topic=topic, metric=metric)
        except BaseInvalidHeadlinesRequestError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response({"value": headline_number})
