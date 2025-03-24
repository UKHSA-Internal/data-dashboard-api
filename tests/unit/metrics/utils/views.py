from rest_framework.serializers import Serializer

from metrics.utils import remove_none_from_serializer_data


def test_remove_none_from_serializer_data_returns_only_non_none_items():
    """
    Given a serializer with data containing `None` values
    When the `remove_none_from_serializer_data()` function is called
    Then the resulting list contains only non-None items
    """
    # Given
    non_communicable = {"theme": "non-communicable", "sub_theme": "respiratory"}
    infectious_disease = {"theme": "infectious_disease", "sub_theme": "respiratory"}

    class DummySerializer(Serializer):

        data = [
            non_communicable,
            None,
            infectious_disease,
            None,
        ]

    serializer = DummySerializer()

    # When
    cleaned_data = remove_none_from_serializer_data(serializer=serializer)

    # Then
    assert len(cleaned_data) == 2
    assert all(item is not None for item in cleaned_data)
    assert cleaned_data == [
        non_communicable,
        infectious_disease,
    ]
