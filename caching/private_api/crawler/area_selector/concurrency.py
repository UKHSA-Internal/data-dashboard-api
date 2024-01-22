import logging
import multiprocessing
import os
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def call_with_star_map_multiprocessing(
    func: Callable, items: list[tuple[Any, Any]]
) -> None:
    """Calls out to the `callable` with the given `items` with a pool of processes

    Notes:
        By default, a pool of N number of processes will be created.
        Where N is equal to the number of CPU cores on the host machine.

    Args:
        func: The callable used to execute the processing of each item
            within the provided iterable
        items: An iterable containing tuples of arguments which
            are to be passed to each individual call within a subprocess

    Returns:
        None

    """
    multiprocessing.set_start_method("spawn", force=True)
    logger.info("Processing with %s No. cores", os.cpu_count())

    with multiprocessing.Pool() as pool:
        pool.starmap(func, items)
