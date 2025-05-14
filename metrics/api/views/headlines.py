from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers.headlines import (
    HeadlinesQuerySerializer,
    HeadlinesResponseSerializer,
)
from metrics.api.serializers.metric_value import MetricValueSerializer
from metrics.domain.headlines.state import Headline
from metrics.domain.models.headline import HeadlineParameters
from metrics.interfaces.headlines.access import (
    BaseInvalidHeadlinesRequestError,
    generate_headline_number,
)

HEADLINES_API_TAG = "headlines"


class HeadlinesView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        parameters=[HeadlinesQuerySerializer],
        responses={HTTPStatus.OK.value: HeadlinesResponseSerializer},
        tags=[HEADLINES_API_TAG],
    )
    @cache_response()
    @require_authorisation
    def get(cls, request, *args, **kwargs):
        """This endpoint can be used to retrieve headline-type numbers.

        ---

        # Main errors

        Note that this endpoint will only return single-headline number type data.
        If the `metric` provided relates to timeseries type data then the request will be deemed invalid.

        ---

        ### Timeseries type metrics are invalid

        For example, a request for the following would be **invalid**:

        - metric =`COVID-19_deaths_ONSByDay`

        - topic = `COVID-19`

        This would be **invalid** because the `metric` of `COVID-19_deaths_ONSByDay` relates to timeseries data,
        which is not represented by a single headline-type figure.

        ---

        Whereas, a request for the following would be **valid**:

        - metric =`COVID-19_headline_ONSdeaths_7DayChange`

        - topic = `COVID-19`

        This would be **valid** because the `metric` of `COVID-19_headline_ONSdeaths_7DayChange`
        relates to headline data, which can be represented by a single headline-type figure.

        Note that the key difference here being the 2nd part of the metric naming methodology:

        *<topic>* *<metric group>* *<description>*

        A valid metric name for this endpoint should include `headline` as the metric group part of the name.

        """
        query_serializer = HeadlinesQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        headline_parameters: HeadlineParameters = query_serializer.to_models(
            request=request
        )

        try:
            headline: Headline = generate_headline_number(
                headline_parameters=headline_parameters
            )
        except BaseInvalidHeadlinesRequestError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={
                    "error_message": str(error)}
            )

        metric_value = MetricValueSerializer.format_to_one_decimal_place(
            headline.metric_value)

        print(f'metric_value: {metric_value}')

        return Response(
            data={
                "value": metric_value,
                "period_end": headline.period_end,
            },
            status=HTTPStatus.OK,
        )
