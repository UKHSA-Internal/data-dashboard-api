from unittest import mock

from metrics.data.operations.ingestion import DEFAULT_BATCH_SIZE, create_core_headlines


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

    def test_delegates_call_to_bulk_create_method_on_model_manager_(self):
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
