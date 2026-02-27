import os
from functools import wraps

from rest_framework.request import Request
from rest_framework.response import Response

from caching.private_api.management import CacheManagement, CacheMissError


class CacheCheckResultedInMissError(Exception): ...


def is_caching_v2_enabled() -> bool:
    return os.environ.get("CACHING_V2_ENABLED", "").lower() in {"true", "1"}


def cache_response(
    *,
    timeout: int | None = None,
    is_reserved_namespace: bool = False,
):
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
            and evicted from the cache.
            If set to `0` the response will not be cached at all.
            If set to `None`, the response will be indefinitely cached,
            until the cache is flushed intentionally.
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

            request = args[1]
            has_jwt = getattr(request, "has_jwt", False)

            is_public = not (has_jwt)

            return _retrieve_response_from_cache_or_calculate(
                view_function,
                timeout,
                is_reserved_namespace,
                is_public,
                *args,
                **kwargs,
            )

        return wrapped_view

    return decorator


def _retrieve_response_from_cache_or_calculate(
    view_function, timeout, is_reserved_namespace, is_public, *args, **kwargs
) -> Response:
    """Gets the response from the cache, otherwise recalculates from the view

    Notes:
        If the `CACHING_V2_ENABLED` env variable is set to "true",
        then the response will always be recalculated from the server
        and no caching will take place.

        If data is not public (i.e. is_public is set to "false"), then the
        response will always be recalculated from the server and no caching
        will take place.

    Args:
        view_function: The view associated with the endpoint
        timeout: The number of seconds after which the response is expired
            and evicted from the cache
        is_reserved_namespace: Boolean switch to store the data
            in the reserved / long-lived namespace within the cache
        *args: args provided by the rest framework middleware
        **kwargs: kwargs provided by the rest framework middleware
            Note that `cache_management` can be injected in through the kwargs

    Returns:
        The response associated with the request

    """
    request: Request = args[1]
    if not is_public:
        return _calculate_response_from_view(view_function, *args, **kwargs)

    if is_caching_v2_enabled() and not is_reserved_namespace:
        return _calculate_response_from_view(view_function, *args, **kwargs)

    cache_management = kwargs.pop(
        "cache_management",
        CacheManagement(in_memory=False, is_reserved_namespace=is_reserved_namespace),
    )
    # It doesn't matter which cache the `CacheManagement` is initially pointed at
    # When we get or save items the `CacheClient` will figure out which cache it needs to go

    cache_entry_key: str = cache_management.build_cache_entry_key_for_request(
        request=request,
        is_reserved_namespace=is_reserved_namespace,
    )

    try:
        return cache_management.retrieve_item_from_cache(
            cache_entry_key=cache_entry_key
        )
    except CacheMissError:
        # If it is not in the cache then we'll write it
        # on the way out after calculating the response
        return _calculate_response_and_save_in_cache(
            view_function, timeout, cache_management, cache_entry_key, *args, **kwargs
        )


def _calculate_response_and_save_in_cache(
    view_function, timeout, cache_management, cache_entry_key, *args, **kwargs
) -> Response:
    response: Response = _calculate_response_from_view(view_function, *args, **kwargs)
    if timeout == 0:
        return response

    cache_management.save_item_in_cache(
        cache_entry_key=cache_entry_key, item=response, timeout=timeout
    )
    return response


def _calculate_response_from_view(view_function, *args, **kwargs) -> Response:
    return view_function(*args, **kwargs)
