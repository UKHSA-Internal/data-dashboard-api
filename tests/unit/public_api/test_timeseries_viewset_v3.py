import pytest
from rest_framework.test import APIRequestFactory

from public_api.version_02.views.timeseries_viewset import APITimeSeriesViewSetV3
from tests.factories.metrics.api_models.time_series import APITimeSeriesFactory


@pytest.mark.django_db
class TestAPITimeSeriesViewSetV3GetQueryset:
    def test_filters_queryset_by_theme_kwarg(self) -> None:
        """
        Ensure `get_queryset` applies the `theme` URL kwarg as a filter.
        """
        # Given: three records with different themes
        infectious_record_1 = APITimeSeriesFactory.create_record(
            theme_name="infectious_disease",
            date="2023-01-01",
        )
        infectious_record_2 = APITimeSeriesFactory.create_record(
            theme_name="infectious_disease",
            date="2023-01-02",
        )
        APITimeSeriesFactory.create_record(
            theme_name="extreme_event",
        )

        # And a view instance with the theme URL kwarg set
        view = APITimeSeriesViewSetV3()
        view.kwargs = {"theme": "infectious_disease"}

        # DRF's GenericAPIView expects a `request` attribute, even though our
        # overridden `get_queryset` does not use it directly.
        view.request = APIRequestFactory().get("/<prefix>/v3/themes/infectious_disease")

        # When
        queryset = view.get_queryset()

        # Then: only records matching the URL theme are returned
        themes = {instance.theme for instance in queryset}
        assert themes == {"infectious_disease"}
        assert queryset.count() == 2
        assert queryset.first() == infectious_record_1
        assert queryset.last() == infectious_record_2
