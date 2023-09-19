from unittest import mock

from ingestion.operations.core_models import (
    DEFAULT_BATCH_SIZE,
    create_core_and_api_timeseries,
    create_core_headlines,
    generate_core_time_series,
)

MODULE_PATH = "ingestion.operations.core_models"


class TestCreateCoreHeadlines:
    def test_delegates_call_to_bulk_create_method_on_model_manager(self):
        """
        Given a list of mocked HeadlineDTOs
        When `create_core_headlines()` is called
        Then the call is delegated to the model manager
        """
        # Given
        spy_core_headline_manager = mock.Mock()
        mocked_core_headline_dtos = [mock.MagicMock()] * 2

        # When
        create_core_headlines(
            headline_dtos=mocked_core_headline_dtos,
            core_headline_manager=spy_core_headline_manager,
        )

        # Then
        expected_core_headline_instances = [
            spy_core_headline_manager.model(
                metric_id=int(mocked_core_headline_dto.metric),
                geography_id=int(mocked_core_headline_dto.geography),
                stratum_id=int(mocked_core_headline_dto.stratum),
                age_id=int(mocked_core_headline_dto.age),
                sex=mocked_core_headline_dto.sex,
                refresh_date=mocked_core_headline_dto.refresh_date,
                period_start=mocked_core_headline_dto.period_start,
                period_end=mocked_core_headline_dto.period_end,
                metric_value=mocked_core_headline_dto.metric_value,
            )
            for mocked_core_headline_dto in mocked_core_headline_dtos
        ]

        spy_core_headline_manager.bulk_create.assert_called_once_with(
            objs=expected_core_headline_instances,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )

    def test_delegates_call_to_bulk_create_method_on_model_manager_with_non_default_batch_size(
        self,
    ):
        """
        Given a non-default value for the `batch_size` parameter
        When `create_core_headlines()` is called
        Then the call delegated to the model manager
            is made with the non-default `batch_size` parameter
        """
        # Given
        non_default_batch_size = 20
        spy_core_headline_manager = mock.Mock()
        mocked_core_headline_dtos = []

        # When
        create_core_headlines(
            headline_dtos=mocked_core_headline_dtos,
            core_headline_manager=spy_core_headline_manager,
            batch_size=non_default_batch_size,
        )

        # Then
        spy_core_headline_manager.bulk_create.assert_called_once_with(
            objs=mocked_core_headline_dtos,
            ignore_conflicts=True,
            batch_size=non_default_batch_size,
        )


class TestGenerateCoreTimeSeries:
    def test_delegates_call_to_bulk_create_method_on_model_manager(self):
        """
        Given a list of mocked CoreTimeSeriesDTOs
        When `generate_core_time_series()` is called
        Then the call is delegated to the model manager
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        mocked_core_time_series_dtos = [mock.MagicMock()] * 2

        # When
        generate_core_time_series(
            timeseries_dtos=mocked_core_time_series_dtos,
            core_time_series_manager=spy_core_time_series_manager,
        )

        # Then
        expected_core_time_series_instances = [
            spy_core_time_series_manager.model(
                metric_id=int(mocked_core_headline_dto.metric),
                geography_id=int(mocked_core_headline_dto.geography),
                stratum_id=int(mocked_core_headline_dto.stratum),
                age_id=int(mocked_core_headline_dto.age),
                sex=mocked_core_headline_dto.sex,
                refresh_date=mocked_core_headline_dto.refresh_date,
                period_start=mocked_core_headline_dto.period_start,
                period_end=mocked_core_headline_dto.period_end,
                metric_value=mocked_core_headline_dto.metric_value,
            )
            for mocked_core_headline_dto in mocked_core_time_series_dtos
        ]

        spy_core_time_series_manager.bulk_create.assert_called_once_with(
            objs=expected_core_time_series_instances,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )

    @mock.patch(f"{MODULE_PATH}._create_core_timeseries_model_instances")
    def test_delegates_call_to_bulk_create_method_on_model_manager_with_non_default_batch_size(
        self,
        spy_create_core_timeseries_model_instances: mock.MagicMock,
    ):
        """
        Given a non-default value for the `batch_size` parameter
        When `generate_core_time_series()` is called
        Then the call delegated to the model manager
            is made with the non-default `batch_size` parameter

        Patches:
            `_create_core_timeseries_model_instances`: To isolate return values
                for the main assertion
        """
        # Given
        non_default_batch_size = 20
        spy_core_time_series_manager = mock.Mock()
        mocked_core_time_series_dtos = [mock.MagicMock()]

        # When
        generate_core_time_series(
            timeseries_dtos=mocked_core_time_series_dtos,
            core_time_series_manager=spy_core_time_series_manager,
            batch_size=non_default_batch_size,
        )

        # Then
        spy_core_time_series_manager.bulk_create.assert_called_once_with(
            objs=spy_create_core_timeseries_model_instances.return_value,
            ignore_conflicts=True,
            batch_size=non_default_batch_size,
        )


class TestCreateCoreAndAPITimeSeries:
    @mock.patch(f"{MODULE_PATH}.generate_core_time_series")
    def test_delegates_call_to_generate_core_time_series(
        self, spy_generate_core_time_series: mock.MagicMock
    ):
        """
        Given mocked DTOs and mocked model managers
        When `create_core_and_api_timeseries()` is called
        Then `generate_core_time_series()` is called with the correct args

        Patches:
            `spy_generate_core_time_series`: For the main assertion
        """
        # Given
        mocked_timeseries_dtos = mock.Mock()
        mocked_core_time_series_manager = mock.Mock()
        mocked_api_time_series_manager = mock.Mock()

        # When
        create_core_and_api_timeseries(
            timeseries_dtos=mocked_timeseries_dtos,
            api_time_series_manager=mocked_api_time_series_manager,
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # Then
        spy_generate_core_time_series.assert_called_once_with(
            timeseries_dtos=mocked_timeseries_dtos,
            core_time_series_manager=mocked_core_time_series_manager,
            batch_size=100,
        )

    @mock.patch(f"{MODULE_PATH}.generate_api_time_series")
    @mock.patch(f"{MODULE_PATH}.generate_core_time_series")
    def test_delegates_call_to_generate_api_time_series(
        self,
        spy_generate_core_time_series: mock.MagicMock,
        spy_generate_api_time_series: mock.MagicMock,
    ):
        """
        Given mocked DTOs and mocked model managers
        When `create_core_and_api_timeseries()` is called
        Then `generate_api_time_series()` is called with the correct args

        Patches:
            `spy_generate_core_time_series`: To isolate the
                return value being passed to `generate_api_time_series()`
            `spy_generate_api_time_series`: For the main assertion
        """
        # Given
        mocked_timeseries_dtos = mock.Mock()
        mocked_core_time_series_manager = mock.Mock()
        mocked_api_time_series_manager = mock.Mock()

        # When
        create_core_and_api_timeseries(
            timeseries_dtos=mocked_timeseries_dtos,
            api_time_series_manager=mocked_api_time_series_manager,
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # Then
        spy_generate_api_time_series.assert_called_once_with(
            all_core_time_series=spy_generate_core_time_series.return_value,
            api_time_series_manager=mocked_api_time_series_manager,
        )
