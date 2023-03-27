from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.data.models.api_models import APITimeSeries
from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data
from metrics.domain.charts.data_visualization import (
    ChartNotSupportedError,
    generate_corresponding_chart,
)


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        """
        This endpoint can be used to generate charts conforming to the UK Gov Design System.
        `topic` relates to the particular disease, wheareas `type` refers to the type of metric (like deaths or cases).

        Currently, the available permutations are:
        | Topic | Type |
        | ----- | ---- |
        | COVID-19 | Vaccinations |
        | Influenza | Healthcare |


        | Topic |
        | ----------- |
        | COVID-19 |
        | Influenza |
        | RSV |
        | Rhinovirus |
        | Parainfluenza |
        | hMPV |
        | Adenovirus |
        | Acute Respiratory Infections |

        Whereas, the available types are:
        | Available types |
        | ----------- |
        | Cases |
        | Deaths |
        | Healthcare |
        | Vaccincations |
        | Testing |

        Note that not all of the above permutations are available.
        Where the given permutation is not available the endpoint will respond with a `HTTP 404 NOT FOUND` error


        """
        chart_type: str = kwargs["type"]
        topic: str = kwargs["topic"]

        try:
            filename: str = generate_corresponding_chart(
                topic=topic, chart_type=chart_type
            )
        except ChartNotSupportedError:
            return Response(status=404)

        image = open(filename, "rb")
        return FileResponse(image)


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="File to be uploaded",
            )
        ],
        deprecated=True,
    )
    def put(self, request, *args, **kwargs):
        """
        Note that this endpoint is **deprecated** and should only be used for demo/testing purposes.
        """
        # CoreTimeSeries.objects.all().delete()
        # APITimeSeries.objects.all().delete()

        load_core_data(filename=request.FILES.get("file"))
        generate_api_time_series()
        return Response(status=204)


class ItemView(View):
    def get(self, request):
        weeklist = []
        datelist = []
        influenzalist = []
        data = APITimeSeries.objects.filter(year=2022).order_by("dt")
        i = 0
        print(len(data))
        disease_list = {
            "Influenza": "weekly_positivity",
            "COVID-19": "weekly_case_count",
            "Parainfluenza": "weekly_positivity",
            "Rhinovirus": "weekly_positivity_by_age",
            "Adenovirus": "weekly_positivity_by_age",
            "RSV": "weekly_positivity_by_age",
            "Acute Respiratory Infections": "weekly_case_count",
        }
        strata = {
            "Influenza": "default",
            "COVID-19": "Pillar 1",
            "Parainfluenza": "default",
            "Rhinovirus": "0 to 4 years",
            "Adenovirus": "0 to 4 years",
            "RSV": "0 to 4 years",
            "Acute Respiratory Infections": "Total outbreaks",
        }
        diseases = {}
        for disease, metric in disease_list.items():
            diseases[disease] = []
        for data_item in data:
            i += 1
            weeklist.append(str(data_item.year) + "-" + str(data_item.epiweek))
            datelist.append(data_item.dt)
            for disease in disease_list:
                if (
                    data_item.topic == disease
                    and data_item.metric == disease_list[disease]
                    and data_item.stratum == strata[disease]
                ):
                    print(
                        f"{disease} metric {disease_list[disease]} value {data_item.metric_value}"
                    )
                    diseases[disease].append(data_item.metric_value)

        weeklist = []
        datelist = []
        data = (
            APITimeSeries.objects.filter(year=2022)
            .filter(topic="Influenza")
            .filter(metric="weekly_positivity")
        )
        i = 0
        for data_item in data:
            i += 1
            weeklist.append(str(data_item.year) + "-" + str(data_item.epiweek))
            datelist.append(data_item.dt)

        diseases["week"] = weeklist
        diseases["dates"] = datelist
        return JsonResponse(diseases)


class GraphView(View):
    def get(self, request, *args, **kwargs):
        points = [
            [0, 494.712664265345],
            [91, 457.4941541268953],
            [182, 434.654725296446],
            [273, 423.29141829658477],
            [364, 342.6589484243782],
            [455, 369.5395702281735],
            [546, 329.6261612244797],
            [637, 268.2713929474297],
            [728, 199.59002475290492],
            [819, 222.7479962573172],
            [910, 55.79834445817295],
            [1001, 187.6533006002134],
        ]
        return HttpResponse(render(request, "graph.html", context={"points": points}))
