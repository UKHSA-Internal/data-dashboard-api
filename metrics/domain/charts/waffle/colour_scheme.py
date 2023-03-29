from typing import List

SUPPORTED_RGB_COLOURS = {
    "light_grey": "216,216,216,1",
    "light_green": "119,196,191,1",
    "middle_green": "0,156,145,1",
    "dark_green": "0,65,61,1",
}


def get_rgb_colour(colour: str) -> str:
    """Gets the RGBA colour representation as required by `plotly`

    Args:
        colour: A human-readable colour.
            >>> 'dark_green'

    Returns:
        str: The RGBA representation.
            >>> 'rgba(0,65,61,1)'

    Raises:
        `KeyError`: If the colour is not supported

    """
    rgb_number = SUPPORTED_RGB_COLOURS[colour]
    return f"rgba({rgb_number})"


class InvalidIdentifierError(Exception):
    ...


def build_color_scale(identifier: int) -> List[List]:
    """Builds the colour scale for the waffle chart plot based on the identifier.

    Args:
        identifier: The position of the plot.
            Currently, this can only be 1, 2 or 3.

    Returns:
        List[list[int, str]]: A nested list of values.
            >>> [
                    [0, 'rgba(216,216,216,1)'],
                    [0.5, 'rgba(0,156,145,1)'],
                    [0.9, 'rgba(0,156,145,1)'],
                    [1, 'rgba(0,156,145,1)'],
            ]

    Raises:
        `InvalidIdentifierError`: If an identifier which is not
            either 1, 2 or 3 is provided.

    """
    background_rgb_colour: str = get_rgb_colour(colour="light_grey")

    if identifier == 3:
        darkest_plot_rgb_colour: str = get_rgb_colour(colour="dark_green")
        return [
            [0, background_rgb_colour],
            [0.5, darkest_plot_rgb_colour],
            [0.9, darkest_plot_rgb_colour],
            [1, darkest_plot_rgb_colour],
        ]

    if identifier == 2:
        middle_plot_rgb_colour: str = get_rgb_colour(colour="middle_green")
        return [
            [0, background_rgb_colour],
            [0.5, middle_plot_rgb_colour],
            [0.9, middle_plot_rgb_colour],
            [1, middle_plot_rgb_colour],
        ]
    if identifier == 1:
        lightest_plot_rgb_colour: str = get_rgb_colour(colour="light_green")
        return [
            [0, background_rgb_colour],
            [0.5, background_rgb_colour],
            [0.9, lightest_plot_rgb_colour],
            [1, lightest_plot_rgb_colour],
        ]

    raise InvalidIdentifierError()
