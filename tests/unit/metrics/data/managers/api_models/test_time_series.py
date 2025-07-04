from unittest import mock

from metrics.data.managers.api_models.time_series import APITimeSeriesManager


class TestAPITimeSeriesManager:
    @mock.patch.object(APITimeSeriesManager, "query_for_superseded_data")
    def test_delete_superseded_data(
        self, spy_query_for_superseded_data: mock.MagicMock
    ):
        """
        Given a payload containing the required fields
            for a dataset slice
        When `delete_superseded_data()` is called
            from an instance of the `APITimeSeriesManager`
        Then the records are retrieved via the
            call made to the `query_for_superseded_data()` method
        And then the retrieved records are deleted
        """
        # Given
        fake_theme = "infectious_disease"
        fake_sub_theme = "respiratory"
        fake_topic = "COVID-19"
        fake_metric = "COVID-19_deaths_ONSByWeek"
        fake_geography = "England"
        fake_geography_type = "Nation"
        fake_geography_code = "E92000001"
        fake_stratum = "default"
        fake_sex = "all"
        fake_age = "all"
        fake_is_public = True

        # When
        APITimeSeriesManager().delete_superseded_data(
            theme=fake_theme,
            sub_theme=fake_sub_theme,
            topic=fake_topic,
            metric=fake_metric,
            geography=fake_geography,
            geography_type=fake_geography_type,
            geography_code=fake_geography_code,
            stratum=fake_stratum,
            sex=fake_sex,
            age=fake_age,
            is_public=fake_is_public,
        )

        # Then
        spy_query_for_superseded_data.assert_called_with(
            theme=fake_theme,
            sub_theme=fake_sub_theme,
            topic=fake_topic,
            metric=fake_metric,
            geography=fake_geography,
            geography_type=fake_geography_type,
            geography_code=fake_geography_code,
            stratum=fake_stratum,
            sex=fake_sex,
            age=fake_age,
            is_public=fake_is_public,
        )

        returned_records = spy_query_for_superseded_data.return_value
        returned_records.delete.assert_called_once()
