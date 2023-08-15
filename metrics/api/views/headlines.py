from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import HeadlinesQuerySerializer
from metrics.api.serializers.headlines import (
    HeadlinesQuerySerializerBeta,
    HeadlinesResponseSerializer,
)
from metrics.domain.models.headline import HeadlineParameters
from metrics.interfaces.headlines.access import (
    BaseInvalidHeadlinesRequestError,
    generate_headline_number,
    generate_headline_number_beta,
)

HEADLINES_API_TAG = "headlines"


class HeadlinesView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        parameters=[HeadlinesQuerySerializer],
        responses={HTTPStatus.OK.value: HeadlinesResponseSerializer},
        tags=[HEADLINES_API_TAG],
        deprecated=True,
    )
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to retrieve headline-type numbers for a given `metric` & `topic` combination.


        **Note this endpoint is now deprecated as it only reference Alpha-scheme data.
        For data using the latest schema, please migrate to `/api/headlines/v3/`**

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

        - metric =`COVID-19_headline_ONSdeaths_7daychange`

        - topic = `COVID-19`

        This would be **valid** because the `metric` of `COVID-19_headline_ONSdeaths_7daychange`
        relates to headline data, which can be represented by a single headline-type figure.

        """
        query_serializer = HeadlinesQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        topic = query_serializer.data["topic"]
        metric = query_serializer.data["metric"]

        try:
            headline_number: str = generate_headline_number(
                topic_name=topic, metric_name=metric
            )
        except BaseInvalidHeadlinesRequestError:
            request_data = request.query_params.dict()
            request_data["geography"] = "England"
            request_data["geography_type"] = "Nation"
            return _handle_beta_schema_headlines_request(request_data=request_data)

        return Response({"value": headline_number})


class HeadlinesViewBeta(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        parameters=[HeadlinesQuerySerializerBeta],
        responses={HTTPStatus.OK.value: HeadlinesResponseSerializer},
        tags=[HEADLINES_API_TAG],
    )
    def get(self, request, *args, **kwargs):
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

        - metric =`COVID-19_headline_ONSdeaths_7daychange`

        - topic = `COVID-19`

        This would be **valid** because the `metric` of `COVID-19_headline_ONSdeaths_7daychange`
        relates to headline data, which can be represented by a single headline-type figure.

        Note that the key difference here being the 2nd part of the metric naming methodology:

        *<topic>* *<metric group>* *<description>*

        A valid metric name for this endpoint should include `headline` as the metric group part of the name.

        """
        return _handle_beta_schema_headlines_request(request_data=request.query_params)


def _handle_beta_schema_headlines_request(request_data):
    query_serializer = HeadlinesQuerySerializerBeta(data=request_data)
    query_serializer.is_valid(raise_exception=True)

    serialized_model: HeadlineParameters = query_serializer.to_models()

    try:
        headline_number: float = generate_headline_number_beta(
            topic_name=serialized_model.topic_name,
            metric_name=serialized_model.metric_name,
            geography_type_name=serialized_model.geography_type_name,
            geography_name=serialized_model.geography_name,
            stratum_name=serialized_model.stratum_name,
            age=serialized_model.age,
            sex=serialized_model.sex,
        )
    except BaseInvalidHeadlinesRequestError as error:
        return Response(
            status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
        )

    return Response({"value": headline_number})