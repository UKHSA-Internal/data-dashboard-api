import logging
from collections.abc import Callable
from multiprocessing.dummy import Pool as ThreadPool
from typing import Any

logger = logging.getLogger(__name__)


def call_with_star_map_multithreading(
    func: Callable,
    items: list[tuple[Any, Any]],
    thread_count: int,
) -> None:
    """Calls out to the `callable` with the given `items` with a pool of threads

    Args:
        func: The callable used to execute the processing of each item
            within the provided iterable
        items: An iterable containing tuples of arguments which
            are to be passed to each individual call
        thread_count: The number of threads to create for the
            execution of the `func` callable with the given `items

    Returns:
        None

    """
    logger.info("Processing with %s No. threads", thread_count)

    with ThreadPool(processes=thread_count) as pool:
        pool.starmap(func=func, iterable=items)
