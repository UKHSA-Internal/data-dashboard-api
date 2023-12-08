from unittest import mock

from ingestion.utils import type_hints
from ingestion.v2.consumer import ConsumerV2
from tests.unit.ingestion.data_transfer_models.test_handlers import (
    DATE_FORMAT,
    DATETIME_FORMAT,
)


class TestBuildModelMethods:
    @mock.patch.object(ConsumerV2, "update_supporting_models")
    def test_build_core_headlines(
        self,
        spy_update_supporting_models: mock.MagicMock,
        example_headline_data_v2: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given fake input data
        When `build_core_headlines()` is called
            from an instance of the `Consumer`
        Then returned `CoreHeadline` instances
            are enriched with the correct values
        """
        # Given
        fake_data = example_headline_data_v2
        fake_data["data"] = [
            {
                "embargo": "2023-11-20 12:00:00",
                "period_start": "2023-10-01",
                "period_end": "2023-10-07",
                "metric_value": 123,
            }
        ]

        consumer = ConsumerV2(source_data=fake_data)

        # When
        core_headline_model_instances = consumer.build_core_headlines()

        # Then
        assert len(core_headline_model_instances) == len(fake_data["data"])
        spy_update_supporting_models.assert_called_once()

        supporting_models_lookup = spy_update_supporting_models.return_value
        built_core_headline_instance = core_headline_model_instances[0]
        assert (
            built_core_headline_instance.metric_id == supporting_models_lookup.metric_id
        )
        assert (
            built_core_headline_instance.geography_id
            == supporting_models_lookup.geography_id
        )
        assert (
            built_core_headline_instance.stratum_id
            == supporting_models_lookup.stratum_id
        )
        assert built_core_headline_instance.age_id == supporting_models_lookup.age_id

        assert built_core_headline_instance.sex == consumer.dto.sex
        assert built_core_headline_instance.refresh_date == consumer.dto.refresh_date

        assert (
            built_core_headline_instance.embargo.strftime(DATETIME_FORMAT)
            == fake_data["data"][0]["embargo"]
        )
        assert (
            built_core_headline_instance.period_start.strftime(DATE_FORMAT)
            == fake_data["data"][0]["period_start"]
        )
        assert (
            built_core_headline_instance.period_end.strftime(DATE_FORMAT)
            == fake_data["data"][0]["period_end"]
        )
        assert (
            built_core_headline_instance.metric_value
            == fake_data["data"][0]["metric_value"]
        )

    @mock.patch.object(ConsumerV2, "update_supporting_models")
    def test_build_core_time_series(
        self,
        spy_update_supporting_models: mock.MagicMock,
        example_time_series_data_v2: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given fake input data
        When `build_core_time_series()` is called
            from an instance of the `Consumer`
        Then returned `CoreTimeSeries` instances
            are enriched with the correct values
        """
        # Given
        fake_data = example_time_series_data_v2
        fake_data["time_series"] = [
            {
                "epiweek": 31,
                "embargo": "2023-11-20 12:00:00",
                "date": "2023-08-01",
                "metric_value": 123,
            }
        ]

        consumer = ConsumerV2(source_data=fake_data)

        # When
        core_time_series_model_instances = consumer.build_core_time_series()

        # Then
        assert len(core_time_series_model_instances) == len(fake_data["time_series"])
        spy_update_supporting_models.assert_called_once()

        supporting_models_lookup = spy_update_supporting_models.return_value
        built_core_time_series_instance = core_time_series_model_instances[0]
        assert (
            built_core_time_series_instance.metric_id
            == supporting_models_lookup.metric_id
        )
        assert (
            built_core_time_series_instance.geography_id
            == supporting_models_lookup.geography_id
        )
        assert (
            built_core_time_series_instance.stratum_id
            == supporting_models_lookup.stratum_id
        )
        assert built_core_time_series_instance.age_id == supporting_models_lookup.age_id
        assert built_core_time_series_instance.sex == consumer.dto.sex
        assert built_core_time_series_instance.refresh_date == consumer.dto.refresh_date
        assert (
            built_core_time_series_instance.metric_frequency
            == consumer.dto.metric_frequency
        )

        assert (
            built_core_time_series_instance.embargo.strftime(DATETIME_FORMAT)
            == fake_data["time_series"][0]["embargo"]
        )
        assert (
            built_core_time_series_instance.date.strftime(DATE_FORMAT)
            == fake_data["time_series"][0]["date"]
        )
        assert built_core_time_series_instance.month == 8
        assert built_core_time_series_instance.year == 2023
        assert (
            built_core_time_series_instance.epiweek
            == fake_data["time_series"][0]["epiweek"]
        )
        assert (
            built_core_time_series_instance.metric_value
            == fake_data["time_series"][0]["metric_value"]
        )

    def test_build_api_time_series(
        self, example_time_series_data_v2: type_hints.INCOMING_DATA_TYPE
    ):
        """
        Given fake input data
        When `build_api_time_series()` is called
            from an instance of the `Consumer`
        Then returned `APITimeSeries` instances
            are enriched with the correct values
        """
        # Given
        fake_data = example_time_series_data_v2
        consumer = ConsumerV2(source_data=fake_data)

        # When
        api_time_series_model_instances = consumer.build_api_time_series()

        # Then
        assert len(api_time_series_model_instances) == len(fake_data["time_series"])

        for index, api_time_series_model_instance in enumerate(
            api_time_series_model_instances
        ):
            assert api_time_series_model_instance.theme == fake_data["parent_theme"]
            assert api_time_series_model_instance.sub_theme == fake_data["child_theme"]
            assert api_time_series_model_instance.topic == fake_data["topic"]
            assert (
                api_time_series_model_instance.metric_group == fake_data["metric_group"]
            )
            assert api_time_series_model_instance.geography == fake_data["geography"]
            assert (
                api_time_series_model_instance.geography_type
                == fake_data["geography_type"]
            )
            assert (
                api_time_series_model_instance.geography_code
                == fake_data["geography_code"]
            )
            assert api_time_series_model_instance.age == fake_data["age"]
            assert api_time_series_model_instance.sex == consumer.dto.sex
            assert api_time_series_model_instance.stratum == fake_data["stratum"]
            assert api_time_series_model_instance.stratum == fake_data["stratum"]
            assert (
                api_time_series_model_instance.metric_frequency
                == consumer.dto.metric_frequency
            )
            assert (
                api_time_series_model_instance.refresh_date == consumer.dto.refresh_date
            )

            assert (
                api_time_series_model_instance.epiweek
                == fake_data["time_series"][index]["epiweek"]
            )
            assert (
                api_time_series_model_instance.date.strftime(DATE_FORMAT)
                == fake_data["time_series"][index]["date"]
            )
            assert (
                api_time_series_model_instance.metric_value
                == fake_data["time_series"][index]["metric_value"]
            )
            assert (
                api_time_series_model_instance.embargo.strftime(DATETIME_FORMAT)
                == fake_data["time_series"][index]["embargo"]
            )
