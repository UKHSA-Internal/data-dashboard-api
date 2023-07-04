from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from public_api.views.base import PUBLIC_API_TAG


class PublicAPIRootView(APIView):
    """
    This is the root of the hyperlinked browsable timeseries API.

    From here you can use the `links` field to guide you to the data that you need.

    Whereby the `themes` field is a hyperlink to all the available **themes**.

    ---

    The data is hierarchical and is structured as follows:

    - -> `theme` - The largest topical subgroup e.g. **infectious_disease**

    - ---> `sub_theme` - A Topical subgroup e.g. **respiratory**

    - -----> `topic` - The name of the topic e.g. **COVID-19**

    - -------> `geography_type` - The type of geography e.g. **Nation**

    - ---------> `geography` - The name of geography associated with metric  e.g. **London**

    - -----------> `metric` - The name of the metric being queried for e.g. **COVID-19_deaths_ONSByDay**

    - -------------> `timeseries` - The final slice of data, which will allow for further filtering via query parameters

    ---

    For example, items stated in bold above would produce the following full URL:

    ```
    .../themes/infectious_disease/sub_themes/respiratory/topics/COVID-19/geography_types/Nation/geographies/London/metrics/COVID-19_deaths_ONSByDay/
    ```

    Note the overall structure of the URL.
    The category is required in plural form, followed by the detail of associated entity.

    For example, `/themes/` is the plural of `theme`.
    This would then be followed by the referring entity, **infectious_disease**

    ---

    The final step in the hierarchy is the `timeseries` endpoint.

    Which will provide the slice of data according to the selected URL parameters.

    At that point, additional query parameters are provided for further granularity and filtering of the data.

    """

    permission_classes = []
    name = "Public API Root"

    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request, format=None):
        data = {
            "links": {
                "themes": reverse("theme-list", request=request, format=format),
            }
        }

        return Response(data)
