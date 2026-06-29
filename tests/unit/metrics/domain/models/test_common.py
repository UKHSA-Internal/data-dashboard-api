import datetime
from types import SimpleNamespace

import pytest
from django.http import HttpRequest
from rest_framework.request import Request

from metrics.domain.models import ChartRequestParams, PlotParameters
from metrics.domain.models.charts.subplot_charts import Subplots
from metrics.domain.models.headline import HeadlineParameters
from metrics.domain.models.map import MapMainParameters, MapsParameters

PERMISSION_SETS = {
    "permission_sets": [{"theme": {"id": "1"}}],
    "summary": {"has_global_access": False},
}

MODEL_FACTORIES = [
    pytest.param(lambda request: _build_models(request)[0], id="headline"),
    pytest.param(lambda request: _build_models(request)[1], id="maps"),
    pytest.param(lambda request: _build_models(request)[2], id="subplots"),
    pytest.param(lambda request: _build_models(request)[3], id="chart_request_params"),
]


def _build_request(*, permission_sets=None) -> Request:
    request = Request(HttpRequest())
    if permission_sets is not None:
        request.user = SimpleNamespace(permission_sets=permission_sets)
    return request


def _build_models(request: Request) -> tuple:
    return (
        HeadlineParameters(
            topic="COVID-19",
            metric="COVID-19_metric",
            geography="England",
            geography_type="Nation",
            stratum="default",
            sex="all",
            age="all",
            request=request,
        ),
        MapsParameters(
            date_from=datetime.date(2025, 1, 1),
            date_to=datetime.date(2025, 12, 31),
            parameters=MapMainParameters(
                theme="infectious_disease",
                sub_theme="respiratory",
                topic="COVID-19",
                metric="COVID-19_metric",
                stratum="default",
                age="all",
                sex="all",
                geography_type="Nation",
                geographies=["England"],
            ),
            accompanying_points=[],
            request=request,
        ),
        Subplots(
            subplot_title="Test subplot",
            x_axis="date",
            y_axis="metric",
            plots=[],
            request=request,
        ),
        ChartRequestParams(
            file_format="svg",
            chart_width=930,
            chart_height=220,
            x_axis="date",
            y_axis="metric",
            plots=[
                PlotParameters(
                    chart_type="bar",
                    topic="COVID-19",
                    metric="COVID-19_metric",
                )
            ],
            request=request,
        ),
    )


@pytest.mark.parametrize(
    "model_factory",
    MODEL_FACTORIES,
)
def test_permission_sets_from_request_user(model_factory):
    request = _build_request(permission_sets=PERMISSION_SETS)
    assert model_factory(request).permission_sets == PERMISSION_SETS


@pytest.mark.parametrize(
    "model_factory",
    MODEL_FACTORIES,
)
def test_permission_sets_default_to_empty_dict(model_factory):
    request = _build_request(permission_sets=None)
    assert model_factory(request).permission_sets == {}
