import json

from plotly.basedatatypes import BaseTraceType


def convert_graph_object_to_dict(*, graph_object: BaseTraceType) -> dict:
    """Converts a plotly graph_object to its corresponding dict representation

    Args:
        graph_object: The graph/plot object to convert.
            This is likely to be a `Scatter` or a `Bar`
            plotly graph object

    Returns:
        Dictionary representation of the graph object

    """
    line_plot = graph_object.to_json(validate=False)
    return json.loads(line_plot)
