from metrics.domain.charts import colour_scheme


class InvalidIdentifierError(Exception):
    ...


def build_color_scale(identifier: int) -> list[list[int, str]]:
    """Builds the colour scale for the waffle chart plot based on the identifier.

    Args:
        identifier: The position of the plot.
            Currently, this can only be 1, 2 or 3.

    Returns:
        list[list[int, str]]: A nested list of values.
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
    background_rgb_colour: str = colour_scheme.RGBAColours.GREY.stringified

    if identifier == 3:
        darkest_plot_rgb_colour: str = colour_scheme.RGBAColours.DARK_GREEN.stringified
        return [
            [0, background_rgb_colour],
            [0.5, darkest_plot_rgb_colour],
            [0.9, darkest_plot_rgb_colour],
            [1, darkest_plot_rgb_colour],
        ]

    if identifier == 2:
        middle_plot_rgb_colour: str = colour_scheme.RGBAColours.MIDDLE_GREEN.stringified
        return [
            [0, background_rgb_colour],
            [0.5, middle_plot_rgb_colour],
            [0.9, middle_plot_rgb_colour],
            [1, middle_plot_rgb_colour],
        ]
    if identifier == 1:
        lightest_plot_rgb_colour: str = (
            colour_scheme.RGBAColours.LIGHT_GREEN.stringified
        )
        return [
            [0, background_rgb_colour],
            [0.5, background_rgb_colour],
            [0.9, lightest_plot_rgb_colour],
            [1, lightest_plot_rgb_colour],
        ]

    raise InvalidIdentifierError
