from unittest import mock

from django.db.models import QuerySet

from metrics.data.access.core_models import _unzip_values

# from metrics.data.access.core_models import get_weekly_disease_incidence


def test_unzip_values():
    """
    Given a list of 3 * 2-item tuples
    When `_unzip_values()` is called
    Then the result is 2 tuples which contain 3 items each
    """
    # Given
    values = [(1, 2), (3, 4), (5, 6)]

    # When
    unzipped_lists = _unzip_values(values)

    # Then
    first_index_item_unzipped_result, second_index_item_unzipped_result = unzipped_lists

    assert first_index_item_unzipped_result == (1, 3, 5)
    assert second_index_item_unzipped_result == (2, 4, 6)


# class TestGetWeeklyDiseaseIncidence:
#     def test_returns_filtered_queryset_casted_to_list(self):
#         """
#         Given a `CoreTimeSeriesManager` and a mocked `QuerySet`.
#         When `get_weekly_disease_incidence() is called.
#         Then the returned object is the filtered `QuerySet`
#             which has been cast to a list.
#         """
#         # Given
#         mocked_core_time_series_manager = mock.Mock()
#         mocked_queryset = mock.MagicMock(spec=QuerySet)
#         mocked_core_time_series_manager.get_metric_values_for_weekly_positivity_by_topic.return_value = (
#             mocked_queryset
#         )
#
#         # When
#         weekly_disease_incidence = get_weekly_disease_incidence(
#             topic=mock.Mock(),  # stubbed
#             core_time_series_manager=mocked_core_time_series_manager,
#         )
#
#         # Then
#         assert weekly_disease_incidence == list(mocked_queryset)
