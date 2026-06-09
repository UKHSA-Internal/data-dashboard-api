# from http import HTTPStatus

# from drf_spectacular.utils import OpenApiExample, extend_schema
# from rest_framework.response import Response

# from caching.private_api.decorators import cache_response
# from metrics.api.decorators.auth import require_authorisation
# from metrics.api.serializers import (
#     DualCategoryDownloadSerializer,
# )
# from metrics.api.views.charts.dual_category_charts import (
#     EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD,
# )
# from metrics.api.views.downloads.common import DOWNLOADS_API_TAG
# from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
# from metrics.interfaces.downloads import access
# from metrics.interfaces.plots.access import DataNotFoundForAnyPlotError

# DEFAULT_VALUE_ERROR_MESSAGE = "Invalid metric_group provided"


# class DualCategoryDownloadsView(SingleCategoryDownloadsView):

#     @extend_schema(
#         request=DualCategoryDownloadSerializer,
#         tags=[DOWNLOADS_API_TAG],
#         examples=[
#             OpenApiExample(
#                 name="COVID-19 age-sex example",
#                 value=EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD,
#                 request_only=True,
#             )
#         ],
#     )
#     @cache_response()
#     @require_authorisation
#     def post(self, request, *args, **kwargs):
#         request_serializer = DualCategoryDownloadSerializer(data=request.data)
#         request_serializer.is_valid(raise_exception=True)

#         file_format: str = request_serializer.data["file_format"]
#         chart_plot_models = request_serializer.to_models(request=request)

#         try:
#             queryset: CoreTimeSeriesQuerySet = access.get_downloads_data(
#                 chart_plots=chart_plot_models
#             )
#         except DataNotFoundForAnyPlotError as error:
#             return Response(
#                 status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
#             )

#         match file_format:
#             case "json":
#                 return self._handle_json(
#                     queryset=queryset, metric_group=chart_plot_models.metric_group
#                 )
#             case "csv":
#                 return self._handle_csv(
#                     queryset=queryset, metric_group=chart_plot_models.metric_group
#                 )
