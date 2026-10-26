import copy
from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from metrics.api.views.tables.subplot_tables.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)

REQUIRED_FIELD_ERROR = ["This field is required."]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/api/charts/v2/",
        "/api/charts/v3/",
        "/api/downloads/v2/",
        "/api/tables/v4/",
    ],
)
def test_plot_validation_errors_are_keyed_by_request_index(path: str):
    """List serializer errors identify invalid plots by their request index."""
    response = APIClient().post(path=path, data={"plots": [{}]}, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST

    plot_errors = response.json()["plots"]
    assert isinstance(plot_errors, dict)
    assert plot_errors["0"]["theme"] == REQUIRED_FIELD_ERROR


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/api/downloads/dual-category/v1/",
        "/api/tables/dual-category/v1/",
    ],
)
def test_segment_validation_errors_are_keyed_by_request_index(path: str):
    """Only invalid dual-category segments appear in the error response."""
    payload = {
        "segments": [
            {"secondary_field_value": "f"},
            {"label": "Missing secondary field value"},
        ]
    }

    response = APIClient().post(path=path, data=payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["segments"] == {
        "1": {"secondary_field_value": REQUIRED_FIELD_ERROR}
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/api/charts/subplot/v1/",
        "/api/downloads/subplot/v1/",
        "/api/tables/subplot/v1/",
    ],
)
def test_nested_subplot_validation_errors_are_keyed_by_request_index(path: str):
    """Nested subplot and plot errors identify both invalid list positions."""
    payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
    del payload["subplots"][0]["plots"][1]["line_colour"]

    response = APIClient().post(path=path, data=payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["subplots"] == {
        "0": {"plots": {"1": {"line_colour": REQUIRED_FIELD_ERROR}}}
    }


@pytest.mark.django_db
def test_metric_value_range_errors_are_keyed_by_request_index():
    """Nested metric value range errors identify the invalid range position."""
    payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
    del payload["chart_parameters"]["metric_value_ranges"][1]["end"]

    response = APIClient().post(
        path="/api/tables/subplot/v1/",
        data=payload,
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["chart_parameters"]["metric_value_ranges"] == {
        "1": {"end": REQUIRED_FIELD_ERROR}
    }


@pytest.mark.django_db
def test_accompanying_point_errors_are_keyed_by_request_index():
    """Map accompanying-point errors identify the invalid point position."""
    response = APIClient().post(
        path="/api/maps/v1/",
        data={"accompanying_points": ["invalid"]},
        format="json",
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    accompanying_point_errors = response.json()["accompanying_points"]
    assert isinstance(accompanying_point_errors, dict)
    assert accompanying_point_errors["0"]["non_field_errors"] == [
        "Invalid data. Expected a dictionary, but got str."
    ]
