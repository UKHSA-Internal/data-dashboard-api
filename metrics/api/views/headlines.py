from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import HeadlinesQuerySerializer
from metrics.api.serializers.headlines import HeadlinesResponseSerializer
from metrics.interfaces.headlines.access import (
    BaseInvalidHeadlinesRequestError,
    generate_headline_number,
)

HEADLINES_API_TAG = "headlines"


class HeadlinesView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        parameters=[HeadlinesQuerySerializer],
        responses={HTTPStatus.OK.value: HeadlinesResponseSerializer},
        tags=[HEADLINES_API_TAG],
    )
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to retrieve headline-type numbers for a given `metric` & `topic` combination.

        ---

        # Main errors

        Note that this endpoint will only return single-headline number type data.
        If the `metric` provided relates to timeseries type data then the request will be deemed invalid.

        ---

        ### Timeseries type metrics are invalid

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
            headline_number: str = generate_headline_number(
                topic_name=topic, metric_name=metric
            )
        except BaseInvalidHeadlinesRequestError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response({"value": headline_number})
