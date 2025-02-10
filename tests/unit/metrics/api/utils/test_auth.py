# import datetime
# import json
# from http import HTTPStatus
# from decimal import Decimal
# from unittest import mock
# from unittest.mock import patch, MagicMock
# import pytest
#
# from rest_framework.test import APIRequestFactory
# from rest_framework.request import Request
#
# from metrics.api.serializers import CoreTimeSeriesSerializer
# from metrics.data.models.core_models.timeseries import CoreTimeSeries
# from metrics.utils.auth import authorised_route
# from metrics.api.views import (
#     DownloadsView,
# )
# from metrics.api.models import (
#     ApiGroup,
#     ApiPermission,
# )
# from metrics.data.models.core_models import (
#     Theme,
#     SubTheme,
# )
#
# @pytest.fixture
# def mock_core_times_series() -> mock.MagicMock:
#     return mock.MagicMock(
#         spec=CoreTimeSeries,
#         metric__topic__sub_theme__theme__name="infectious_disease",
#         metric__topic__sub_theme__name="respiratory",
#         metric__topic__name="COVID-19",
#         metric__name="COVID-19_cases_rateRollingMean",
#         geography__name="England",
#         geography__geography_type__name="Nation",
#         stratum__name="default",
#         age__name="all",
#         sex="all",
#         year=2024,
#         date=datetime.date(day=1, month=1, year=2024),
#         metric_value=Decimal("1.000"),
#     )
#
#
# @pytest.fixture
# def api_group_mock():
#     """Fixture to return a fake ApiGroup instance with permissions."""
#     mock_group = MagicMock()
#     theme1 = Theme.objects.create(name="theme1")
#     theme2 = Theme.objects.create(name="theme2")
#     subtheme1 = SubTheme.objects.create(name="subtheme1", theme=theme1)
#     subtheme2 = SubTheme.objects.create(name="subtheme2", theme=theme2)
#     api_permissions = ApiPermission.objects.create(
#         name="permission1",
#         theme=theme1,
#         sub_theme=subtheme1,
#     )
#     api_permissions2 = ApiPermission.objects.create(
#         name="permission2",
#         theme=theme2,
#         sub_theme=subtheme2,
#     )
#     group1 = ApiGroup.objects.create(name="group1")
#     group2 = ApiGroup.objects.create(name="group2")
#     group1.permissions.set([api_permissions])
#     group2.permissions.set([api_permissions2])
#     group1.save()
#     group2.save()
#     mock_group.permissions.all.return_value = (group1, group2)
#     return mock_group
#
#
# @pytest.fixture
# def mock_jwt_decode():
#     """Fixture to mock JWT decode function."""
#     with patch("jwt.decode") as mock:
#         mock.return_value = {"group_id": "test-group"}
#         yield mock
#
#
# @pytest.fixture
# def mock_api_group_get(api_group_mock):
#     """Fixture to mock ApiGroup.objects.get() method."""
#     with patch("metrics.api.models.ApiGroup.objects.get") as mock:
#         mock.return_value = api_group_mock
#         yield mock
#
#
# class TestAuth:
#
#     def setup_method(self):
#         self.factory = APIRequestFactory()
#
#
#     serialized_data = [
#         {
#             "theme": "infectious_disease",
#             "sub_theme": "respiratory",
#             "topic": "COVID-19",
#             "geography_type": "Nation",
#             "geography": "England",
#             "metric": "COVID-19_cases_rateRollingMean",
#             "age": "all",
#             "stratum": "default",
#             "sex": "f",
#             "year": 2023,
#             "date": "2023-11-08",
#             "metric_value": "8.9900",
#             "in_reporting_delay_period": False,
#         },
#     ]
#
#     headers = {"Authorization": "Bearer VALID_TOKEN"}
#     body = {
#           "file_format": "json",
#           "plots": [
#             {
#               "metric": "COVID-19_cases_rateRollingMean",
#               "topic": "COVID-19",
#               "stratum": "default",
#               "age": "all",
#               "sex": "f",
#               "geography": "England",
#               "geography_type": "Nation",
#               "date_from": "2000-01-01",
#               "date_to": "2025-01-28"
#             },
#             {
#               "metric": "asthma_syndromic_emergencyDepartment_countsByDay",
#               "topic": "asthma",
#               "stratum": "default",
#               "age": "all",
#               "sex": "all",
#               "geography": "",
#               "geography_type": "",
#               "date_from": "2000-01-01",
#               "date_to": "2025-01-28"
#             }
#           ]
#         }
#
#
#     @pytest.mark.skip
#     @pytest.mark.django_db
#     def test_t(
#             self,
#             mock_core_times_series: mock.MagicMock,
#             mock_jwt_decode,
#             mock_api_group_get,
#     ):
#         django_request = self.factory.post(
#             "/api/downloads/v2",
#             data=json.dumps(self.body),
#             headers=self.headers,
#             content_type="application/json",
#         )
#         view = DownloadsView.as_view()
#         response = view(django_request)
#
#         assert response.status_code is not None
