from unittest import mock

from ingestion.operations.batch_record_creation import create_records


class TestCreateRecords:
    def test_delegates_calls_successfully(self):
        """
        Given a list of model instances and a batch size integer
        When `create_records()` is called
        Then the call is delegated to the `bulk_create()`
            method on the model manager with the correct args
        """
        # Given
        mocked_model_instances = [mock.Mock()] * 3
        spy_model_manager = mock.Mock()
        batch_size = 50

        # When
        create_records(
            model_instances=mocked_model_instances,
            model_manager=spy_model_manager,
            batch_size=batch_size,
        )

        # Then
        spy_model_manager.bulk_create.assert_called_once_with(
            objs=mocked_model_instances,
            ignore_conflicts=True,
            batch_size=batch_size,
        )
