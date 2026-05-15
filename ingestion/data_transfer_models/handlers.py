from collections.abc import Callable

from ingestion.data_transfer_models.headline import (
    HeadlineDTO,
    _build_enriched_headline_specific_fields,
    _build_headline_dto,
)
from ingestion.data_transfer_models.time_series import (
    TimeSeriesDTO,
    _build_enriched_time_series_specific_fields,
    _build_time_series_dto,
)
from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from validation.data_transfer_models.base import MissingFieldError
from validation.is_public import validate_is_public


def build_time_series_dto_from_source(
    *,
    source_data: INCOMING_DATA_TYPE,
    filename: str,
) -> TimeSeriesDTO:
    """
    Enriches a `TimeSeriesDTO` with the corresponding fields from the `source_data`

    Args:
        source_data: The incoming source data to be validated
        filename: The incoming filename, eg "my_file.json"

    Returns:
        An enriched `InboundTimeSeriesDTO`

    Raises:
        `MissingFieldError`: If a field which was expected
            to be found in the `source_data` could not be found.
            i.e. it would otherwise have raised a `KeyError`
        `ValueError`: If the "time_series" value is given as None
        `ValidationError`: If any of the fields do not conform
            to the underlying validation checks
    """
    return _build_dto_from_source(
        source_data=source_data,
        filename=filename,
        key_for_specific_fields="time_series",
        extract_specific_fields_function=_build_enriched_time_series_specific_fields,
        build_dto_function=_build_time_series_dto,
    )


def build_headline_dto_from_source(
    *, source_data: INCOMING_DATA_TYPE, filename: str
) -> HeadlineDTO:
    """
    Enriches a `HeadlineDTO` with the corresponding fields from the `source_data`

    Args:
        source_data: The incoming source data to be validated
        filename: The incoming filename, eg "my_file.json"

    Returns:
        An enriched `InboundTimeSeriesDTO`

    Raises:
        `MissingFieldError`: If a field which was expected
            to be found in the `source_data` could not be found.
            i.e. it would otherwise have raised a `KeyError`
        `ValueError`: If the "time_series" value is given as None
        `ValidationError`: If any of the fields do not conform
            to the underlying validation checks
    """
    return _build_dto_from_source(
        source_data=source_data,
        filename=filename,
        key_for_specific_fields="data",
        extract_specific_fields_function=_build_enriched_headline_specific_fields,
        build_dto_function=_build_headline_dto,
    )


def _build_dto_from_source(
    *,
    source_data: INCOMING_DATA_TYPE,
    filename: str,
    key_for_specific_fields: str,
    extract_specific_fields_function: Callable,
    build_dto_function: Callable,
) -> TimeSeriesDTO | HeadlineDTO:
    # Try and extract the list of specific fields models
    # If it is not there, raise an error early
    try:
        incoming_individual_specific_fields = source_data[key_for_specific_fields]
    except KeyError as error:
        raise MissingFieldError(field=error.args[0]) from error

    # If that same field was provided as None, raise an error
    if incoming_individual_specific_fields is None:
        raise ValueError

    # ValueErrors raised inside function
    validate_is_public(
        source_data=source_data,
        fields=incoming_individual_specific_fields,
        filename=filename,
    )

    # Using the injected `extract_specific_fields_function`
    # try and extract a list of enriched models for the specific fields
    try:
        enriched_specific_fields = extract_specific_fields_function(
            source_data=source_data
        )
    except KeyError as error:
        raise MissingFieldError(field=error.args[0]) from error

    # Build the full DTO which nests the previously created specific fields models
    try:
        return build_dto_function(
            source_data=source_data,
            enriched_specific_fields=enriched_specific_fields,
        )
    except KeyError as error:
        raise MissingFieldError(field=error.args[0]) from error
