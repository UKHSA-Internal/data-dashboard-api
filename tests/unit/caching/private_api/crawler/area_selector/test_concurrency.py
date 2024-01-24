from unittest import mock

from caching.private_api.crawler.area_selector.concurrency import (
    call_with_star_map_multiprocessing,
)

MODULE_PATH = "caching.private_api.crawler.area_selector.concurrency"


class TestCallWithMultiprocessing:
    @mock.patch(f"{MODULE_PATH}.multiprocessing")
    def test_call_with_multiprocessing_sets_method_of_spawn(
        self, spy_multiprocessing: mock.MagicMock
    ):
        """
        Given a mocked callable
        When `call_with_star_map_multiprocessing()` is called
        Then the multiprocessing library is set to "spawn"
            child processes

        Patches:
            `spy_multiprocessing`: To check that the context is set
                with child processes "spawned" instead of forked
                and force=True is provided to bypass the `RuntimeError`
                which gets raise by the library
                when the method is set multiple times

        """
        # Given
        mocked_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # When
        call_with_star_map_multiprocessing(func=mocked_callable, items=mocked_items)

        # Then
        spy_multiprocessing.set_start_method.assert_called_once_with(
            "spawn", force=True
        )

    @mock.patch(f"{MODULE_PATH}.multiprocessing")
    def test_call_with_multiprocessing_pool(self, spy_multiprocessing: mock.MagicMock):
        """
        Given a mocked callable and a list of items
        When `call_with_star_map_multiprocessing()` is called
        Then the call is delegated to the `starmap()` method
            on the multiprocessing `Pool` object

        Patches:
            `spy_multiprocessing`: To check that the pool of
                child processes are created and mapped accordingly

        """
        # Given
        mocked_callable = mock.Mock()
        mocked_items = [mock.Mock()]

        # When
        call_with_star_map_multiprocessing(func=mocked_callable, items=mocked_items)

        # Then
        expected_calls = [
            mock.call(),
            mock.call().__enter__(),
            mock.call().__enter__().starmap(mocked_callable, mocked_items),
            mock.call().__exit__(None, None, None),
        ]
        spy_multiprocessing.Pool.assert_has_calls(calls=expected_calls)
