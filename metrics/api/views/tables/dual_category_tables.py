from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers.tables import (
    DualCategoryTableRequestParamsSerializer,
    TablesResponseSerializer,
)
from metrics.api.views.tables.common import TABLES_API_TAG
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)
from metrics.interfaces.tables import access


class DualCategoryTablesView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=DualCategoryTableRequestParamsSerializer,
        responses={HTTPStatus.OK.value: TablesResponseSerializer},
        tags=[TABLES_API_TAG],
    )
    @require_authorisation
    @cache_response()
    def post(cls, request, *args, **kwargs):
        """This endpoint can be used to generate chart data in tabular format."""
        request_serializer = DualCategoryTableRequestParamsSerializer(data=request.data)
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
