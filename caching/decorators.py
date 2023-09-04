from functools import wraps

from rest_framework.request import Request
from rest_framework.response import Response

from caching.management import CacheManagement, CacheMissError


def cache_response():
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

    Returns:
        The response containing the results of the request.
        Note that the results could be retrieved from the cache
        or calculated from the server

    """

    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs) -> Response:
            return retrieve_response_from_cache_or_calculate(
                view_function, *args, **kwargs
            )

        return wrapped_view

    return decorator


def retrieve_response_from_cache_or_calculate(
    view_function, *args, **kwargs
) -> Response:
    """Gets the response from the cache, otherwise recalculates from the view

    Args:
        view_function: The view associated with the endpoint
        *args: args provided by the rest framework middleware
        **kwargs: kwargs provided by the rest framework middleware
            Note that `cache_management` can be injected in through the kwargs

    Returns:
        The response associated with the request

    """

    request: Request = args[1]
    cache_management = kwargs.pop("cache_management", CacheManagement(in_memory=True))

    cache_entry_key: str = cache_management.build_cache_entry_key_for_request(
        request=request
    )

    try:
        return cache_management.retrieve_item_from_cache(
            cache_entry_key=cache_entry_key
        )
    except CacheMissError:
        response: Response = _calculate_response_from_view(
            view_function, *args, **kwargs
        )
        cache_management.save_item_in_cache(
            cache_entry_key=cache_entry_key, item=response
        )
        return response


def _calculate_response_from_view(view_function, *args, **kwargs) -> Response:
    return view_function(*args, **kwargs)
