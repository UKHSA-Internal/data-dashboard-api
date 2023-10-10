from unittest import mock

from ingestion.operations.concurrency import (
    call_with_multiprocessing,
    run_with_multiple_processes,
)

MODULE_PATH = "ingestion.operations.concurrency"


class TestRunWithMultiprocessing:
    @mock.patch(f"{MODULE_PATH}.call_with_multiprocessing")
    def test_delegates_call_successfully(
        self, spy_call_with_multiprocessing: mock.MagicMock
    ):
        """
        Given a mocked callable used for the upload
        When `run_with_multiple_processes()` is called
        Then the call is delegated to `call_with_multiprocessing()`

        Patches:
            `spy_call_with_multiprocessing` To check that the callable
                is passed to this call

        """
        # Given
        mocked_upload_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # When
        run_with_multiple_processes(
            upload_function=mocked_upload_callable, items=mocked_items
        )

        # Then
        spy_call_with_multiprocessing.assert_called_once_with(
            upload_function=mocked_upload_callable, items=mocked_items
        )


class TestCallWithMultiprocessing:
    @mock.patch(f"{MODULE_PATH}.multiprocessing")
    def test_call_with_multiprocessing_sets_method_of_spawn(
        self, spy_multiprocessing: mock.MagicMock
    ):
        """
        Given a mocked callable used for the upload
        When `_call_with_multiprocessing()` is called
        Then the multiprocessing library is set to "spawn"
            child processes.

        Patches:
            `spy_multiprocessing`: To check that the context is set
                with child processes "spawned" instead of forked

        """
        # Given
        mocked_upload_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # When
        call_with_multiprocessing(
            upload_function=mocked_upload_callable, items=mocked_items
        )

        # Then
        spy_multiprocessing.set_start_method.assert_called_once_with("spawn")

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
