"""Tests for the is_public / data_classification fields across all chart serializers.

These fields are the API entry-point for the watermark feature:
    - /api/charts/v2        (ChartsSerializer / EncodedChartsRequestSerializer)
    - /api/charts/v3        (ChartsSerializer / EncodedChartsRequestSerializer)
"""

from unittest import mock

from rest_framework.request import Request

from metrics.api.serializers.charts import (
    ChartsSerializer,
    EncodedChartsRequestSerializer,
)
from metrics.api.serializers.charts.single_category_charts import ChartPlotSerializer
from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.api.serializers.headlines import HeadlinesQuerySerializer
from metrics.api.serializers.trends import TrendsQuerySerializer
from metrics.domain.models import ChartRequestParams, PlotParameters
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.data_classification.access import DataClassificationInterface

_MINIMAL_CHARTS_PAYLOAD = {"file_format": "svg", "plots": []}
_REQUEST = mock.Mock(spec=Request)


def _make_minimal_subplot_payload() -> dict:
    return {
        "file_format": "svg",
        "chart_parameters": {
            "x_axis": "stratum",
            "y_axis": "metric",
            "theme": "Respiratory",
            "sub_theme": "Flu",
            "date_from": "2023-01-01",
            "date_to": "2023-12-31",
        },
        "subplots": [],
    }


class TestChartsSerializerIsPublicField:
    def test_is_public_defaults_to_true(self):
        """
        Given a payload without an `is_public` field
        When `is_valid()` is called on `ChartsSerializer`
        Then `is_public` defaults to True
        """

        serializer = ChartsSerializer(data=_MINIMAL_CHARTS_PAYLOAD)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["is_public"] is True

    def test_is_public_accepts_false(self):
        """
        Given a payload with `is_public=False`
        When `is_valid()` is called on `ChartsSerializer`
        Then validation succeeds and `is_public` is False
        """

        payload = {**_MINIMAL_CHARTS_PAYLOAD, "is_public": False}
        serializer = ChartsSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["is_public"] is False

    def test_data_classification_defaults_to_none_when_not_provided(self):
        """
        Given a payload without a `data_classification` field
        When `is_valid()` is called on `ChartsSerializer`
        Then `data_classification` defaults to None
        """

        serializer = ChartsSerializer(data=_MINIMAL_CHARTS_PAYLOAD)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["data_classification"] is None

    def test_data_classification_accepts_non_default_value_from_our_list(self):
        """
        Given a payload with a custom `data_classification` string
        When `is_valid()` is called on `ChartsSerializer`
        Then the custom value is preserved
        """

        payload = {**_MINIMAL_CHARTS_PAYLOAD, "data_classification": "SECRET"}
        serializer = ChartsSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["data_classification"] == "SECRET"


class TestChartsSerializerToModelsDataClassification:
    def test_to_models_passes_is_public_true_by_default(self):
        """
        Given a payload without `is_public` or `data_classification`
        When `to_models()` is called
        Then the resulting `ChartRequestParams` has `is_public=True`
            and `data_classification=None`
        """

        serializer = ChartsSerializer(data=_MINIMAL_CHARTS_PAYLOAD)
        serializer.is_valid(raise_exception=True)
        params: ChartRequestParams = serializer.to_models(request=_REQUEST)
        assert params.is_public is True
        assert params.data_classification is None

    def test_to_models_resolves_default_data_classification_when_is_public_false(self):
        """
        Given `is_public=False` with no explicit `data_classification`
        When `to_models()` is called
        Then `data_classification` is set to DEFAULT_DATA_CLASSIFICATION
        """

        payload = {**_MINIMAL_CHARTS_PAYLOAD, "is_public": False}
        serializer = ChartsSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: ChartRequestParams = serializer.to_models(request=_REQUEST)
        assert params.is_public is False
        assert params.data_classification == DataClassificationInterface.DEFAULT

    def test_to_models_uses_explicit_data_classification_when_is_public_false(self):
        """
        Given `is_public=False` and an explicit `data_classification`
        When `to_models()` is called
        Then the provided `data_classification` is used (not the default)
        """

        payload = {
            **_MINIMAL_CHARTS_PAYLOAD,
            "is_public": False,
            "data_classification": "TOP SECRET",
        }
        serializer = ChartsSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: ChartRequestParams = serializer.to_models(request=_REQUEST)
        assert params.data_classification == "TOP SECRET"

    def test_to_models_data_classification_is_none_when_is_public_true(self):
        """
        Given `is_public=True` and no explicit `data_classification`
        When `to_models()` is called
        Then `data_classification` remains None (no default applied)
        """

        payload = {**_MINIMAL_CHARTS_PAYLOAD, "is_public": True}
        serializer = ChartsSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: ChartRequestParams = serializer.to_models(request=_REQUEST)
        assert params.data_classification is None


class TestEncodedChartsRequestSerializerDataClassification:
    def test_is_public_field_is_present(self):
        """
        Given a payload without `is_public`
        When `is_valid()` is called on `EncodedChartsRequestSerializer`
        Then `is_public` defaults to True
        """

        payload = {"file_format": "svg", "plots": []}
        serializer = EncodedChartsRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["is_public"] is True

    def test_resolves_default_data_classification_when_not_public(self):
        """
        Given `is_public=False` with no explicit `data_classification`
        When `to_models()` is called on `EncodedChartsRequestSerializer`
        Then `data_classification` is resolved to DEFAULT_DATA_CLASSIFICATION
        """

        payload = {"file_format": "svg", "plots": [], "is_public": False}
        serializer = EncodedChartsRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: ChartRequestParams = serializer.to_models(request=_REQUEST)
        assert params.data_classification == DataClassificationInterface.DEFAULT


class TestSubplotChartRequestSerializerDataClassification:
    def test_is_public_defaults_to_true(self):
        """
        Given a payload without `is_public`
        When `is_valid()` is called on `SubplotChartRequestSerializer`
        Then `is_public` defaults to True
        """

        payload = _make_minimal_subplot_payload()
        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["is_public"] is True

    def test_is_public_accepts_false(self):
        """
        Given `is_public=False`
        When `is_valid()` is called on `SubplotChartRequestSerializer`
        Then validation succeeds with `is_public=False`
        """

        payload = {**_make_minimal_subplot_payload(), "is_public": False}
        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["is_public"] is False

    def test_resolves_default_data_classification_when_not_public(self):
        """
        Given `is_public=False` with no explicit `data_classification`
        When `to_models()` is called on `SubplotChartRequestSerializer`
        Then `data_classification` is resolved to DEFAULT_DATA_CLASSIFICATION
        """

        payload = {**_make_minimal_subplot_payload(), "is_public": False}
        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: SubplotChartRequestParameters = serializer.to_models(request=_REQUEST)
        assert params.is_public is False
        assert params.data_classification == DataClassificationInterface.DEFAULT

    def test_uses_explicit_data_classification_when_not_public(self):
        """
        Given `is_public=False` and an explicit `data_classification`
        When `to_models()` is called on `SubplotChartRequestSerializer`
        Then the explicit value is used
        """

        payload = {
            **_make_minimal_subplot_payload(),
            "is_public": False,
            "data_classification": "RESTRICTED",
        }
        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: SubplotChartRequestParameters = serializer.to_models(request=_REQUEST)
        assert params.data_classification == "RESTRICTED"

    def test_data_classification_is_none_when_public(self):
        """
        Given `is_public=True` (or omitted) with no `data_classification`
        When `to_models()` is called on `SubplotChartRequestSerializer`
        Then `data_classification` is None
        """

        payload = _make_minimal_subplot_payload()
        serializer = SubplotChartRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        params: SubplotChartRequestParameters = serializer.to_models(request=_REQUEST)
        assert params.data_classification is None
