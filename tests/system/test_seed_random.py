from urllib.parse import quote

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models.supporting import Geography, Metric
from metrics.data.models.core_models.timeseries import CoreTimeSeries

EXPECTED_METRIC_COUNT = 10
EXPECTED_GEOGRAPHY_COUNT = 5
EXPECTED_TIME_SERIES_COUNT = 1_500
HTTP_OK = 200


class TestSeedRandomCommand:
    @pytest.mark.django_db
    def test_command_seeds_metrics_dataset_and_data_is_queryable_via_api(self):
        """
        Given an empty metrics dataset
        When the `seed_random` management command is run for small metrics scale
        Then the expected amount of data is inserted
        And it can be queried from the public tables API endpoint
        """
        # Given
        assert Metric.objects.count() == 0
        assert Geography.objects.count() == 0
        assert CoreTimeSeries.objects.count() == 0
        assert APITimeSeries.objects.count() == 0

        # When
        call_command(
            "seed_random",
            dataset="metrics",
            scale="small",
            seed=12345,
            truncate_first=True,
        )

        # Then
        assert Metric.objects.count() == EXPECTED_METRIC_COUNT
        assert Geography.objects.count() == EXPECTED_GEOGRAPHY_COUNT
        assert CoreTimeSeries.objects.count() == EXPECTED_TIME_SERIES_COUNT
        assert APITimeSeries.objects.count() == EXPECTED_TIME_SERIES_COUNT

        sample_row = APITimeSeries.objects.order_by("id").first()
        assert sample_row is not None

        api_client = APIClient()
        path = (
            "/api/public/timeseries/"
            f"themes/{quote(sample_row.theme, safe='')}/"
            f"sub_themes/{quote(sample_row.sub_theme, safe='')}/"
            f"topics/{quote(sample_row.topic, safe='')}/"
            f"geography_types/{quote(sample_row.geography_type, safe='')}/"
            f"geographies/{quote(sample_row.geography, safe='')}/"
            "metrics/"
        )
        response = api_client.get(
            path=path,
            format="json",
            HTTP_ACCEPT="application/json",
        )

        assert response.status_code == HTTP_OK
        assert "metrics" in response.data
        assert sample_row.metric in response.data["metrics"]
