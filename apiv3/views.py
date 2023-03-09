from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apiv3.api_models import WeeklyTimeSeries
from apiv3.models import TimeSeries, upload_data
from domain.charts.data_visualization import write_chart_file_for_topic


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        """
        This endpoint can be used to generate charts conforming to the UK Gov Design System.
        `topic` relates to the particular disease.

        Currently, the available topics are:

        - `COVID-19`

        - `Influenza`

        - `RSV`

        - `Rhinovirus`

        - `Parainfluenza`

        - `hMPV`

        - `Adenovirus`

        - `Acute Respiratory Infections`

        """
        filename = write_chart_file_for_topic(topic=kwargs["topic"])

        image = open(filename, 'rb')
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
        ]
    )
    def put(self, request, *args, **kwargs):
        TimeSeries.objects.all().delete()
        with open(kwargs["filename"], "wb+") as destination:
            for chunk in request.FILES["file"].chunks():
                destination.write(chunk)
        with open(kwargs["filename"], "r") as source:
            upload_data(data=source)
        return Response(status=204)


class ItemView(View):
    def get(self, request):
        weeklist = []
        datelist = []
        influenzalist = []
        data = WeeklyTimeSeries.objects.filter(year=2022).order_by('start_date')
        i = 0
        print(len(data))
        disease_list = {
            "Influenza": "weekly_positivity",
            "COVID-19": "weekly_case_count",
            "Parainfluenza": "weekly_positivity",
            "Rhinovirus": "weekly_positivity_by_age",
            "Adenovirus": "weekly_positivity_by_age",
            "RSV": "weekly_positivity_by_age",
            "Acute Respiratory Infections": "weekly_case_count"

        }
        strata = {
            "Influenza": "default",
            "COVID-19": "Pillar 1",
            "Parainfluenza": "default",
            "Rhinovirus": "0 to 4 years",
            "Adenovirus": "0 to 4 years",
            "RSV": "0 to 4 years",
            "Acute Respiratory Infections": "Total outbreaks"
        }
        diseases = {}
        for disease, metric in disease_list.items():
            diseases[disease] = []
        for data_item in data:
            i += 1
            weeklist.append(str(data_item.year) + "-" + str(data_item.epiweek))
            datelist.append(data_item.start_date)
            for disease in disease_list:
                if data_item.topic == disease and data_item.metric == disease_list[disease] and data_item.stratum == strata[disease]:
                    print(f"{disease} metric {disease_list[disease]} value {data_item.metric_value}")
                    diseases[disease].append(data_item.metric_value)

        weeklist = []
        datelist = []
        data = WeeklyTimeSeries.objects.filter(year=2022).filter(topic="Influenza").filter(metric="weekly_positivity")
        i = 0
        for data_item in data:
            i += 1
            weeklist.append(str(data_item.year) + "-" + str(data_item.epiweek))
            datelist.append(data_item.start_date)

        diseases["week"] = weeklist
        diseases["dates"] = datelist
        return JsonResponse(diseases)

class GraphView(View):
    def get(self, request, *args, **kwargs):
        points = [[0, 494.712664265345], [91, 457.4941541268953], [182, 434.654725296446], [273, 423.29141829658477],
                  [364, 342.6589484243782], [455, 369.5395702281735], [546, 329.6261612244797], [637, 268.2713929474297],
                  [728, 199.59002475290492], [819, 222.7479962573172], [910, 55.79834445817295], [1001, 187.6533006002134]]
        return HttpResponse(render(request, "graph.html", context={"points": points}))
