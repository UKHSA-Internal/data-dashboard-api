import logging
from collections.abc import Mapping, Sequence

from metrics.api.settings.auth import ALLOW_MISSING_IS_PUBLIC_FIELD

NON_PUBLIC_DATA_PREFIX = "OFF-SENS_"

NOT_METRIC_ERROR = "No top-level metric field"
FILE_AND_DATA_IS_PUBLIC_MISMATCH_ERROR = "Files prefixed with OFF-SENS_ must contain only is_public=False data and files without that prefix must contain only is_public=True data."
IS_PUBLIC_BOOLEAN_ERROR = "Every is_public value must be provided as a boolean."
MIXED_IS_PUBLIC_VALUES_ERROR = "A file must not contain a combination of is_public=True and is_public=False values."
METRIC_AND_DATA_IS_PUBLIC_MISMATCH_ERROR = "Metrics prefixed with OFF-SENS_ must contain only is_public=False data and unprefixed metrics must contain only is_public=True data."
MISSING_IS_PUBLIC_FIELD_ERROR = (
    "The is_public field is missing from the inbound source data."
)

logger = logging.getLogger(__name__)


def validate_is_public(
    *,
    source_data: Mapping[str, object],
    fields: Sequence[Mapping[str, object]],
    filename: str,
) -> None:
    """
    Validation rules are explained in each function below

    Args:
        source_data: Top-level file payload (metric payload) to validate
        fields: Lower-level objects to validate (= entries from data/time_series nodes)
        filename: Filename to validate is_public rules against, eg
                  "my_headline.json" or "OFF-SENS_my_headline.json".
    """

    is_metric_non_public = _is_metric_off_sens(source_data=source_data)
    is_metric_public = not is_metric_non_public

    _does_metric_off_sens_match_filename(
        filename=filename, is_metric_public=is_metric_public
    )

    common_is_public_value = _is_is_public_consistent_in_data_fields(
        fields=fields, filename=filename
    )

    # After this, we have also implicitly tested, that filename matches is_public
    _does_metric_off_sens_match_first_is_public(
        is_public=common_is_public_value, is_metric_public=is_metric_public
    )


def _is_metric_off_sens(*, source_data: Mapping[str, object]) -> bool:
    """
    True if metric starts off with "OFF-SENS_", else false
    """

    metric = source_data.get("metric")

    # Sanity check
    if not isinstance(metric, str):
        raise TypeError(NOT_METRIC_ERROR)

    # Actual check
    return metric.startswith(NON_PUBLIC_DATA_PREFIX)


def _does_metric_off_sens_match_filename(
    *, filename: str, is_metric_public: bool
) -> None:
    """
    True if both metric and filename start off with "OFF-SENS_", or none of them
    """

    expected_is_public = not filename.startswith(NON_PUBLIC_DATA_PREFIX)

    if is_metric_public is not expected_is_public:
        raise ValueError(FILE_AND_DATA_IS_PUBLIC_MISMATCH_ERROR)


def _is_is_public_consistent_in_data_fields(
    *, fields: Sequence[Mapping[str, object]], filename: str
) -> bool | None:
    """
    Each lower-level object must provide an is_public field.
    No missing values. No non-boolean values.
    Returns the single consistent is_public value, or None if there are no fields.
    """

    if not fields:
        return None

    is_public_values: list[bool] = []

    for field in fields:
        if "is_public" not in field:
            raise ValueError(MISSING_IS_PUBLIC_FIELD_ERROR)

        is_public = field["is_public"]

        if not isinstance(is_public, bool):
            raise TypeError(IS_PUBLIC_BOOLEAN_ERROR)

        is_public_values.append(is_public)

    # They must not mix is_public=True and is_public=False
    all_is_public_values = set(is_public_values)

    if len(all_is_public_values) > 1:
        raise ValueError(MIXED_IS_PUBLIC_VALUES_ERROR)

    return all_is_public_values.pop() if all_is_public_values else None


def _does_metric_off_sens_match_first_is_public(
    *, is_public: bool | None, is_metric_public: bool
) -> None:
    """
    True if both metric starts off with "OFF-SENS_" and is_public=false (or vice versa)
    """

    if is_public is None:
        return

    if is_public != is_metric_public:
        raise ValueError(METRIC_AND_DATA_IS_PUBLIC_MISMATCH_ERROR)

