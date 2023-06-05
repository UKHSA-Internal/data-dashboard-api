from rest_framework import viewsets

from metrics.public_api.metrics_interface.interface import MetricsPublicAPIInterface
from metrics.public_api.serializers.timeseries_serializers import (
    APITimeSeriesListSerializer,
)


class APITimeSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint will provide the full timeseries of a slice of data.

    There are a set of mandatory URL parameters and optional query parameters:

    Note that by default, results are paginated by a page size of 5.

    ---

    Whereby the mandatory URL parameters are as follows in order from first to last:

    - `theme` - The Largest topical subgroup e.g. **infectious_disease**

    - `sub_theme` - A Topical subgroup e.g. **respiratory**

    - `topic` - The name of the topic e.g. **COVID-19**

    - `geography_type` - The type of geography e.g. **Nation**

    - `geography` - The name of geography associated with metric  e.g. **London**

    - `metric` - The name of the metric being queried for e.g. **new_cases_daily**


    ---

    From here you can filter the data further via a set of optional query parameters:

    - `stratum` - Smallest subgroup a metric can be broken down into e.g. **15_44** for the age group of 15-44 years

    - `sex` - Patient gender e.g. **F** for Female or **ALL** for all genders

    - `year` - Epi year of the metrics value (important for annual metrics) e.g. **2020**

    - `epiweek` - Epi week of the metric value (important for weekly metrics) e.g. **30**

    - `dt` - The date which this metric value was recorded in the format **YYYY-MM-DD** e.g. **2020-07-20**

    """

    queryset = (
        MetricsPublicAPIInterface.get_api_timeseries_model()
        .objects.all()
        .order_by("dt")
    )
    serializer_class = APITimeSeriesListSerializer
