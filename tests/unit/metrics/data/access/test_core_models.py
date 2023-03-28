from unittest import mock

from django.db.models import QuerySet

# from metrics.data.access.core_models import get_weekly_disease_incidence

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
