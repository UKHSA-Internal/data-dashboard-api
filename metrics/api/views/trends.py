from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import TrendsQuerySerializer, TrendsResponseSerializer
from metrics.api.serializers.trends import TrendsQuerySerializerBeta
from metrics.domain.models.trends import TrendsParameters
from metrics.domain.trends.state import TREND_AS_DICT
from metrics.interfaces.trends.access import (
    TrendNumberDataNotFoundError,
    generate_trend_numbers,
    generate_trend_numbers_beta,
)

TRENDS_API_TAG = "trends"


class TrendsView(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        parameters=[TrendsQuerySerializer],
        responses={HTTPStatus.OK.value: TrendsResponseSerializer},
        tags=[TRENDS_API_TAG],
    )
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to retrieve trend-type data for a given `topic`, `metric` and `percentage_metric` combination.

        The response will include data to indicate whether the change should be considered positive.

        Primarily, this is because an increase in metric value requires additional context whether it should be considered positive.

        For example, an increase in cases would be considered negative.
        But an increase in vaccinations would be considered positive.

        ---

        # Main errors

        Note that this endpoint will only key-value pair type data for the trend block.
        If the provided parameters return data which does not exist then this will be invalid.

        ---

        ## Data could not be found

        For example, a request for the following would be **invalid**:

        - topic = `Influenza`

        - metric =`COVID-19_headline_ONSdeaths_7daychange`

        - percentage_metric =`COVID-19_headline_ONSdeaths_7daypercentchange`

        This would be **invalid** because the `metric` of `COVID-19_headline_ONSdeaths_7daychange`
        and a topic of `Influenza` will not return any data.

        """
        query_serializer = TrendsQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        topic: str = query_serializer.data["topic"]
        metric_name: str = query_serializer.data["metric"]
        percentage_metric_name: str = query_serializer.data["percentage_metric"]

        try:
            trends_data: TREND_AS_DICT = generate_trend_numbers(
                topic=topic,
                metric_name=metric_name,
                percentage_metric_name=percentage_metric_name,
            )
        except TrendNumberDataNotFoundError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(trends_data)


class TrendsViewBeta(APIView):
    permission_classes = [HasAPIKey]

    @extend_schema(
        parameters=[TrendsQuerySerializerBeta],
        responses={HTTPStatus.OK.value: TrendsResponseSerializer},
        tags=[TRENDS_API_TAG],
    )
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to retrieve trend-type data for a given `topic`, `metric` and `percentage_metric` combination.

        The response will include data to indicate whether the change should be considered positive.

        Primarily, this is because an increase in metric value requires additional context whether it should be considered positive.

        For example, an increase in cases would be considered negative.
        But an increase in vaccinations would be considered positive.

        ---

        # Main errors

        Note that this endpoint will only key-value pair type data for the trend block.
        If the provided parameters return data which does not exist then this will be invalid.

        ---

        ## Data could not be found

        For example, a request for the following would be **invalid**:

        - topic = `Influenza`

        - metric =`COVID-19_headline_ONSdeaths_7daychange`

        - percentage_metric =`COVID-19_headline_ONSdeaths_7daypercentchange`

        This would be **invalid** because the `metric` of `COVID-19_headline_ONSdeaths_7daychange`
        and a topic of `Influenza` will not return any data.

        """
        query_serializer = TrendsQuerySerializerBeta(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        serialized_model: TrendsParameters = query_serializer.to_models()

        try:
            trends_data: TREND_AS_DICT = generate_trend_numbers_beta(
                topic_name=serialized_model.topic_name,
                metric_name=serialized_model.metric_name,
                percentage_metric_name=serialized_model.percentage_metric_name,
                geography_name=serialized_model.geography_name,
                geography_type_name=serialized_model.geography_type_name,
                stratum_name=serialized_model.stratum_name,
                sex=serialized_model.sex,
                age=serialized_model.age,
            )
        except TrendNumberDataNotFoundError as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(trends_data)
