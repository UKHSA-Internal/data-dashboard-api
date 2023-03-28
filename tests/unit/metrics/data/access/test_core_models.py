from metrics.data.access.core_models import unzip_values


def test_unzip_values():
    """
    Given a list of 3 * 2-item tuples
    When `unzip_values()` is called
    Then the result is 2 tuples which contain 3 items each
    """
    # Given
    values = [(1, 2), (3, 4), (5, 6)]

    # When
    unzipped_lists = unzip_values(values)

    # Then
    first_index_item_unzipped_result, second_index_item_unzipped_result = unzipped_lists

    assert first_index_item_unzipped_result == (1, 3, 5)
    assert second_index_item_unzipped_result == (2, 4, 6)
