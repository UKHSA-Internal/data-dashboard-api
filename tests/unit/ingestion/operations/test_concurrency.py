from unittest import mock

from ingestion.operations.concurrency import (
    call_with_multiprocessing,
    run_with_multiple_processes,
)

MODULE_PATH = "ingestion.operations.concurrency"


class TestRunWithMultiprocessing:
    @mock.patch(f"{MODULE_PATH}.call_with_multiprocessing")
    @mock.patch(f"{MODULE_PATH}.db")
    def test_closes_db_connections_from_first(
        self, spy_db: mock.MagicMock, spy_call_with_multiprocessing: mock.MagicMock
    ):
        """
        Given a mocked callable used for the upload
        When `run_with_multiple_processes()` is called
        Then the database connections are closed
            before `_call_with_multiprocessing()` is called

        Patches:
            `spy_db`: To check that `django.db.connections.close_all()`
                is called before `_call_with_multiprocessing()`

            `spy_call_with_multiprocessing` To check that the callable
                is passed to this call after database connections have been pre-closed

        """
        # Given
        mocked_upload_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # Set up a mock manager, so we can record calls made from both `spy_db` and `spy_call_with_multiprocessing`
        mock_manager = mock.Mock()
        mock_manager.attach_mock(spy_db, "spy_db")
        mock_manager.attach_mock(
            spy_call_with_multiprocessing, "spy_call_with_multiprocessing"
        )

        # When
        run_with_multiple_processes(
            upload_function=mocked_upload_callable, items=mocked_items
        )

        # Then
        expected_calls = [
            mock.call.spy_db.connections.close_all(),
            mock.call.spy_call_with_multiprocessing(
                upload_function=mocked_upload_callable, items=mocked_items
            ),
        ]
        mock_manager.assert_has_calls(calls=expected_calls, any_order=False)


class TestCallWithMultiprocessing:
    @mock.patch(f"{MODULE_PATH}.multiprocessing")
    def test_call_with_multiprocessing_sets_method_of_fork(
        self, spy_multiprocessing: mock.MagicMock
    ):
        """
        Given a mocked callable used for the upload
        When `_call_with_multiprocessing()` is called
        Then the multiprocessing library is set to "fork"
            child processes.

        Patches:
            `spy_multiprocessing`: To check that the context is set
                with child processes "forked" instead of spawned

        """
        # Given
        mocked_upload_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # When
        call_with_multiprocessing(
            upload_function=mocked_upload_callable, items=mocked_items
        )

        # Then
        spy_multiprocessing.set_start_method.assert_called_once_with("fork")

    @mock.patch(f"{MODULE_PATH}.multiprocessing")
    def test_call_with_multiprocessing_pool(self, spy_multiprocessing: mock.MagicMock):
        """
        Given a mocked callable used for the upload
        When `call_with_multiprocessing()` is called
        Then the call is delegated to the `map()` method
            on the multiprocessing `Pool` object

        Patches:
            `spy_multiprocessing`: To check that the pool of
                child processes are created and mapped accordingly

        """
        # Given
        mocked_upload_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # When
        call_with_multiprocessing(
            upload_function=mocked_upload_callable, items=mocked_items
        )

        # Then
        expected_calls = [
            mock.call(),
            mock.call().__enter__(),
            mock.call().__enter__().map(mocked_upload_callable, mocked_items),
            mock.call().__exit__(None, None, None),
        ]
        spy_multiprocessing.Pool.assert_has_calls(calls=expected_calls)
