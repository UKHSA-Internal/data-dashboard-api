from unittest import mock

from caching.common.multi_threading import call_with_star_map_multithreading

MODULE_PATH = "caching.common.multi_threading"


class TestCallWithStarMapMultiThreading:
    @mock.patch(f"{MODULE_PATH}.ThreadPool")
    def test_has_expected_calls(self, spy_thread_pool: mock.MagicMock):
        """
        Given a mocked callable, a list of items and a thread count
        When `call_with_star_map_multithreading()` is called
        Then the call is delegated to the `starmap()` method
            on the multiprocessing.dummy `Pool` object

        Patches:
            `spy_thread_pool`: To check that the pool of
                threads are created and mapped accordingly

        """
        # Given
        mocked_callable = mock.Mock()
        mocked_items = [mock.Mock()]
        thread_count = 50

        # When
        call_with_star_map_multithreading(
            func=mocked_callable,
            items=mocked_items,
            thread_count=thread_count,
        )

        # Then
        expected_calls = [
            mock.call(processes=thread_count),
            mock.call().__enter__(),
            mock.call()
            .__enter__()
            .starmap(func=mocked_callable, iterable=mocked_items),
            mock.call().__exit__(None, None, None),
        ]
        spy_thread_pool.assert_has_calls(calls=expected_calls)
