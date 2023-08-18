def _check_values(values: list[int]) -> None:
    if len(values) > 3:
        raise TooManyDataPointsError()

    values_in_descending_order: list[int] = sorted(values, reverse=True)
    # Checks that the values are in descending order going from largest -> smallest
    # This check ensures that the largest value is not drawn with a darker colour
    # Which would in turn obfuscate the other plots
    if values != values_in_descending_order:
        raise DataPointsNotInDescendingOrderError()


class TooManyDataPointsError(Exception):
    ...


class DataPointsNotInDescendingOrderError(Exception):
    ...
