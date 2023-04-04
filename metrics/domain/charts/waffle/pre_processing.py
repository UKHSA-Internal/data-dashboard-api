import logging

from numpy import NaN
from numpy.core.multiarray import ndarray, zeros

logger = logging.getLogger(__name__)


def build_two_dimensional_matrix(
    threshold: int, identifier: int, length: int = 10, width: int = 10
) -> ndarray:
    """Builds a 2D matrix with the `identifier` as the non-zero value.

    Notes:
        If the `identifier` is not given as `1`,
        then all non-zero values will become `NaN` values.
        The `length` and `width` default to 10.
        This means that by default the returned matrix will be
        of size `100`.

    Examples:
        >>> build_two_dimensional_matrix(threshold=1, identifier=1, length=2, width=2)
        array([[1., 0.], [0., 0.]])

        >>> build_two_dimensional_matrix(threshold=4, identifier=1, length=3, width=3)
        array([[1., 1., 1.], [1., 0., 0.], [0., 0., 0.]])

        >>> build_two_dimensional_matrix(threshold=1, identifier=2, length=2, width=2)
        array([[2., nan.], [nan., nan.]])

        >>> build_two_dimensional_matrix(threshold=1, identifier=3, length=2, width=2)
        array([[3., nan.], [nan., nan.]])

    Args:
        threshold: The nominal point of non-zero values in the matrix
        identifier: The number to assign to the non-zero values.
        length: The size in the y-axis to build the matrix to.
            Defaults to 10
        width: The size in the x-axis to build the matrix to.
            Defaults to 10

    Returns:
        np.ndarray: A 2D array of the shape dicated
        by the given `length` and `width` values.
        E.g. With the following:
            identifier = 1
            length = 2
            width = 2
            threshold = 2
        >>> array([[1., 1.], [0., 0.]])

    """
    matrix_size: int = length * width
    data: ndarray = zeros(shape=matrix_size)

    if identifier > 1:
        data[:] = NaN

    data[:threshold] = identifier
    return data.reshape([width, length])
