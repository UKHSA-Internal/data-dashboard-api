from collections.abc import Callable

from metrics.domain.utils import _check_for_substring_match

URL_PATTERN_HINT = tuple[str, str, str, Callable]


PATHS_TO_HIDE_FROM_SWAGGER: tuple[str] = ("cms-admin",)


def pre_processing_endpoint_filter_hook(
    endpoints: list[URL_PATTERN_HINT],
) -> list[URL_PATTERN_HINT]:
    """Pre-processing hook used in conjunction with drf-spectacular to hide endpoints from swagger

    Args:
        endpoints: List of urlpattern endpoints
            injected by the parent preproccesing hook

    Returns:
        A list of filtered endpoints

    """
    filtered_endpoints = []

    for path, path_regex, method, callback in endpoints:
        path_is_ignored: bool = _check_for_substring_match(
            string_to_check=path, substrings=PATHS_TO_HIDE_FROM_SWAGGER
        )

        if not path_is_ignored:
            filtered_endpoints.append((path, path_regex, method, callback))

    return filtered_endpoints
