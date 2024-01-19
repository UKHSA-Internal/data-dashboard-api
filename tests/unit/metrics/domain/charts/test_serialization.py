import plotly

from metrics.domain.charts.serialization import convert_graph_object_to_dict


class TestConvertGraphObjectToDict:
    def test_returns_correct_dict(self):
        """
        Given a plotly `Scatter` graph object
        When `convert_graph_object_to_dict()` is called
        Then the corresponding dict representation is returned
        """
        # Given
        graph_object = plotly.graph_objects.Scatter(
            x=(1, 2, 3),
            y=(4, 5, 6),
            name="Test",
        )

        # When
        serialized_graph_object: dict = convert_graph_object_to_dict(
            graph_object=graph_object
        )

        # Then
        assert type(serialized_graph_object) is dict
        assert tuple(serialized_graph_object["x"]) == graph_object.x
        assert tuple(serialized_graph_object["y"]) == graph_object.y
        assert serialized_graph_object["type"] == graph_object.type
        assert serialized_graph_object["name"] == graph_object.name
