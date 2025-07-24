import os
from functools import wraps

from rest_framework.request import Request
from rest_framework.response import Response

from caching.internal_api_client import (
    CACHE_CHECK_HEADER_KEY,
    CACHE_FORCE_REFRESH_HEADER_KEY,
)
from caching.private_api.management import CacheManagement, CacheMissError


class CacheCheckResultedInMissError(Exception): ...


def is_caching_v2_enabled() -> bool:
    return os.environ.get("CACHING_V2_ENABLED", "").lower() in {"true", "1"}


def cache_response(timeout: int | None = None, is_reserved_namespace: bool = False):
    """Decorator to wrap API views to use a previously cached response. Otherwise, calculate and save on the way out.

    Notes:
        This custom decorator is implemented so that
        we can cache `POST` endpoints as well as `GET` endpoints.
        Typically, we wouldn't want to cache `POST` endpoints.
        Our `charts`, `tables` and `downloads` endpoints are all `POST` endpoints.
        In reality, the only reason for them to be `POST` endpoints is down
        to the request payload.
        For all intents and purposes, they behave like `GET` endpoints.
        Hence, the decision was made to create this custom decorator to cache them.
        Since, the out-of-the-box cache decorators do not implement the ability
        to cache `POST` endpoints.

    Args:
        timeout: The number of seconds after which the response is expired
            and evicted from the cache
        is_reserved_namespace: Boolean switch to store the data
            in the reserved / long-lived namespace within the cache.
            Defaults to `False`.

    Returns:
        The response containing the results of the request.
        Note that the results could be retrieved from the cache
        or calculated from the server

    """

    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs) -> Response:
            return _retrieve_response_from_cache_or_calculate(
                view_function, timeout, is_reserved_namespace, *args, **kwargs
            )

        return wrapped_view

    return decorator


def _retrieve_response_from_cache_or_calculate(
    view_function, timeout, is_reserved_namespace, *args, **kwargs
) -> Response:
    """Gets the response from the cache, otherwise recalculates from the view

    Notes:
        If the "Cache-Force-Refresh" header is set to True,
        then the response will be recalculated from the server
        and this will overwrite the corresponding entry in the cache

        If the `CACHING_V2_ENABLED` env variable is set to "true",
        then the response will always be recalculated from the server
        and no caching will take place.

    Args:
        view_function: The view associated with the endpoint
        timeout: The number of seconds after which the response is expired
            and evicted from the cache
        is_reserved_namespace: Boolean switch to store the data
            in the reserved / long-lived namespace within the cache.
            Defaults to `False`.
        *args: args provided by the rest framework middleware
        **kwargs: kwargs provided by the rest framework middleware
            Note that `cache_management` can be injected in through the kwargs

    Returns:
        The response associated with the request

    """

    request: Request = args[1]

    if is_caching_v2_enabled():
        return _calculate_response_from_view(view_function, *args, **kwargs)

    cache_management = kwargs.pop("cache_management", CacheManagement(in_memory=False))

    cache_entry_key: str = cache_management.build_cache_entry_key_for_request(
        request=request, is_reserved_namespace=is_reserved_namespace
    )

    if request.headers.get(CACHE_FORCE_REFRESH_HEADER_KEY, False):
        # If the `Cache-Force-Refresh` is True
        # recalculate & save regardless of whether the item exists in the cache
        return _calculate_response_and_save_in_cache(
            view_function, timeout, cache_management, cache_entry_key, *args, **kwargs
        )

    try:
        return cache_management.retrieve_item_from_cache(
            cache_entry_key=cache_entry_key
        )
    except CacheMissError as error:
        # If the `Cache-Check` header is True
        # and there has been 1 cache miss, then error out early
        if request.headers.get(CACHE_CHECK_HEADER_KEY, False):
            raise CacheCheckResultedInMissError from error

        return _calculate_response_and_save_in_cache(
            view_function, timeout, cache_management, cache_entry_key, *args, **kwargs
        )


def _calculate_response_and_save_in_cache(
    view_function, timeout, cache_management, cache_entry_key, *args, **kwargs
) -> Response:
    response: Response = _calculate_response_from_view(view_function, *args, **kwargs)
    cache_management.save_item_in_cache(
        cache_entry_key=cache_entry_key, item=response, timeout=timeout
    )
    return response


def _calculate_response_from_view(view_function, *args, **kwargs) -> Response:
    return view_function(*args, **kwargs)
