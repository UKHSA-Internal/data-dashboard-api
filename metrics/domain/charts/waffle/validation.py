from typing import List


def _check_data_points(data_points: List[int]) -> None:
    if len(data_points) > 3:
        raise TooManyDataPointsError()

    data_points_in_descending_order: List[int] = sorted(data_points, reverse=True)
    # Checks that the data_points are in descending order going from largest -> smallest
    # This check ensures that the largest value is not drawn with a darker colour
    # Which would in turn obfuscate the other plots
    if data_points != data_points_in_descending_order:
        raise DataPointsNotInDescendingOrderError()


class TooManyDataPointsError(Exception):
    ...


class DataPointsNotInDescendingOrderError(Exception):
    ...
