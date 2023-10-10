import logging
import multiprocessing
import os
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)


def run_with_multiple_processes(upload_function: Callable, items: list[str]) -> None:
    """Executes the `upload_function` with the given `items` with a pool of processes

    Args:
        upload_function: The callable used to execute the ingestion of each item
        items: A list of strings which can be understood by the `upload_function`
            For example, if the `upload_function` expects a path, then this
            will be a list of paths.

    Returns:
        None

    """
    logger.info("Spawning processes for ingestion")

    start_time = time.perf_counter()

    call_with_multiprocessing(upload_function=upload_function, items=items)

    finish_time = time.perf_counter()
    time_elapsed = round(finish_time - start_time, 2)

    logger.info(
        "Completed upload in %s seconds - using %s No. processes",
        time_elapsed,
        os.cpu_count(),
    )


def call_with_multiprocessing(upload_function: Callable, items: list[str]) -> None:
    """Calls out to the `upload_function` with the given `items` with a pool of processes

    Notes:
        By default, a pool of N number of processes will be created.
        Where N is equal to the number of CPU cores on the host machine.

    Args:
        upload_function: The callable used to execute the ingestion of each item
        items: A list of strings which can be understood by the `upload_function`
            For example, if the `upload_function` expects a path, then this
            will be a list of paths.

    Returns:
        None

    """
    multiprocessing.set_start_method("spawn")

    logger.info("Starting upload with %s No. cores", os.cpu_count())
    with multiprocessing.Pool() as pool:
        pool.map(upload_function, items)
