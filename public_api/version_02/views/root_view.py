from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from public_api.version_02.views.base import PUBLIC_API_TAG


class PublicAPIRootViewV2(APIView):
    """
    **Using the API**

    Use the API to extract and save data from the UKHSA data dashboard.
    To start, please select and filter to the specific data metric you’re interested in.

    The hyperlinked API will guide you to the data you’re looking for.
    By clicking on each link, you’ll be shown the next options available for the data you’ve selected.
    The data selection is structured, meaning the option you select will determine the options available.

    ---

    This is how the data is structured:

    - Theme – the overall subgroup of the data. For example, **infectious_disease**

    - Sub_theme – the group the data falls in within the theme. For example, **respiratory**

    - Topic – the type of data within the sub-theme. For example, **COVID-19**

    - Geography_type – the type of geographical area for the data. For example, **NHS region**

    - Geography – the specific geographical area related to the type. For example, **London**

    - Metric – the name of the metric you’re interested in. For example, **COVID-19_cases_casesByDay**

    - Timeseries – further filtering of the data

    ---

    The structure of the URL stays the same for each API query, following the filtering selection process.
    For example, the data filtering shown above (in bold) would produce this URL:

    ```
    /themes/infectious_disease/sub_themes/respiratory/topics/COVID-19/geography_types/NHS_region/geographies/London/metrics/COVID-19_cases_casesByDay
    ```

    The overall category is plural (in this example, themes)
    which is then followed by the detail selected (in this example, infectious_diseases).

    Unlike the coronavirus (COVID-19) dashboard API, you cannot extract all the data across a topic or geography type.
    The API is designed for you to be selective by data type, topic, geography and metric.

    """

    permission_classes = []
    name = "API"

    @classmethod
    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(cls, request, format=None):
        data = {
            "links": {
                "themes": reverse("theme-list-v2", request=request, format=format),
            }
        }

        return Response(data)
