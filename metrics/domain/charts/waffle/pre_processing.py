def reshape(flat_list: list[int], length: int, width: int) -> list[list[int | str]]:
    """Given a (1D) list along with a length and width returns a 2D list

    Args:
        flat_list: flat list of values to be reshaped as a 2D list (matrix)
        length: integer representing the length (columns) of the matrix
        width: integer representing the width (rows) of the matrix

    Returns:
        A 2D list of values using 'width' for row length
    """
    index = 0
    matrix = []
    while index < length * width:
        matrix.append(flat_list[index : index + width])
        index += width
    return matrix


def build_two_dimensional_matrix(
    threshold: int, identifier: int, length: int = 10, width: int = 10
) -> list[list[int | str]]:
    """Builds a 2D matrix with the 'identifier' as the non-zero value.

    Examples:
        >>> build_two_dimensional_matrix(threshold=1, identifier=1, length=2, width=2)
        array([[1, 0], [0, 0]])

        >>> build_two_dimensional_matrix(threshold=4, identifier=1, length=3, width=3)
        array([[1, 1, 1], [1, 0, 0], [0, 0, 0]])

        >>> build_two_dimensional_matrix(threshold=1, identifier=2, length=2, width=2)
        array([[2, 'NaN'], ['NaN', 'NaN']])

        >>> build_two_dimensional_matrix(threshold=1, identifier=3, length=2, width=2)
        array([[3, 'NaN'], ['NaN', 'NaN']])

    Args:
        threshold: represents the list position / number of non-zero values
        identifier: represents the non-zero value.
        length: the length (colum size) of the matrix defaults to 10
        width:  the width (row size) of the matrix default to 10

    Returns:
        A 2D list with the shape derived from the length and width
    """
    matrix_size: int = length * width
    data = [0] * matrix_size

    if identifier > 1:
        data[:] = ["NaN"] * matrix_size

    data[:threshold] = [identifier] * threshold
    return reshape(data, length, width)
