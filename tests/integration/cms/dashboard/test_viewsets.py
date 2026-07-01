import os
from http import HTTPStatus
from unittest import mock

import pytest
from django.test import RequestFactory
from rest_framework.request import Request
from rest_framework.test import APIClient
from wagtail.models import Page

from cms.common.models import CommonPage
from cms.dashboard.viewsets import CMSPagesAPIViewSet
from cms.metrics_documentation.models.child import MetricsDocumentationChildEntry
from cms.topic.models import TopicPage
from metrics.data.models.core_models import Metric, Topic


class MockPermissionSets(list):
    def __init__(self, permissions, has_global_access=False, total_permission_sets=0):
        super().__init__(permissions)
        self._summary = {
            "has_global_access": has_global_access,
            "total_permission_sets": total_permission_sets,
        }

    def __getitem__(self, key):
        if key == "permission_sets":
            return list(self)
        if key == "summary":
            return self._summary
        return super().__getitem__(key)


@pytest.mark.django_db
class TestCMSPagesAPIViewSetPermissions:

    @pytest.fixture
    def setup_pages(self):
        influenza_topic = Topic.objects.create(name="Influenza")
        metric = Metric.objects.create(
            name="influenza_headline_positivityLatest", topic=influenza_topic
        )

        covid_topic = Topic.objects.create(name="COVID-19")
        private_metric = Metric.objects.create(
            name="COVID-19_headline_cases_7DayTotals", topic=covid_topic
        )
        private_metric_two = Metric.objects.create(
            name="COVID-19_headline_7DayAdmissionsChange", topic=covid_topic
        )

        home = Page.objects.get(id=2)

        public_topic = TopicPage(
            title="Public Topic",
            page_description="test",
            slug="public-topic",
            is_public=True,
            theme="1",
            seo_title="public-topic",
        )
        home.add_child(instance=public_topic)

        private_topic = TopicPage(
            title="Private Topic",
            page_description="test",
            slug="private-topic",
            is_public=False,
            theme="1",
            sub_theme="test",
            topic="test",
            page_classification="official_sensitive",
            seo_title="private-topic",
        )
        home.add_child(instance=private_topic)

        public_metrics = MetricsDocumentationChildEntry(
            title="Public Metric",
            page_description="test",
            slug="public-metric",
            metric=metric.pk,
            is_public=True,
            seo_title="public-metrics",
        )
        home.add_child(instance=public_metrics)

        private_metrics = MetricsDocumentationChildEntry(
            title="Private Metric",
            page_description="test",
            slug="private-metric",
            theme="2",
            sub_theme="test",
            topic="test",
            metric=private_metric.pk,
            is_public=False,
            seo_title="private-metrics",
        )
        home.add_child(instance=private_metrics)

        private_metrics_two = MetricsDocumentationChildEntry(
            title="Private Metric 2",
            page_description="test",
            slug="private-metric-two",
            theme="1",
            sub_theme="test",
            topic="test",
            metric=private_metric_two.pk,
            is_public=False,
            seo_title="private-metrics-two",
        )
        home.add_child(instance=private_metrics_two)

        standard_page = CommonPage(
            title="Standard", body="test", slug="standard", seo_title="standard-page"
        )
        home.add_child(instance=standard_page)

        return {
            "public_topic": public_topic,
            "private_topic": private_topic,
            "public_metrics": public_metrics,
            "private_metrics": private_metrics,
            "standard_page": standard_page,
        }

    @mock.patch(f"cms.dashboard.viewsets.AUTH_ENABLED", True)
    def test_anonymous_user_access(self, setup_pages):
        """
        Given a request is made by an unauthenticated user
        When the queryset is retrieved
        Then only public pages are returned
        """
        # Given
        rf = RequestFactory()
        url = "/api/v2/pages/"
        django_request = rf.get(url)

        request = Request(django_request)

        mock_user = mock.MagicMock()
        request.user = mock_user

        view = CMSPagesAPIViewSet()
        view.request = request

        # When
        result = view.get_queryset()

        # Then
        titles = [p.title for p in result]
        assert "Public Topic" in titles
        assert "Public Metric" in titles
        assert "Standard" in titles
        assert "Private Topic" not in titles
        assert "Private Metric" not in titles
        assert "Private Metric 2" not in titles

    @mock.patch(f"cms.dashboard.viewsets.AUTH_ENABLED", True)
    def test_global_access_user(self, setup_pages):
        """
        Given a request is made by an authenticated user with global access
        When the queryset is retrieved
        Then all pages are returned
        """
        # Given
        rf = RequestFactory()
        url = "/api/v2/pages/"
        django_request = rf.get(url)

        request = Request(django_request)

        mock_user = mock.MagicMock()
        mock_user.permission_sets = MockPermissionSets(
            [],
            has_global_access=True,
        )

        request.user = mock_user
        request.auth = "token"

        view = CMSPagesAPIViewSet()
        view.request = request

        # When
        result = view.get_queryset()

        # Then
        titles = [p.title for p in result]
        assert "Public Topic" in titles
        assert "Public Metric" in titles
        assert "Standard" in titles
        assert "Private Topic" in titles
        assert "Private Metric" in titles
        assert "Private Metric 2" in titles

    @mock.patch(f"cms.dashboard.viewsets.AUTH_ENABLED", True)
    def test_restricted_user_with_permission(self, setup_pages):
        """
        Given a request is made by an authenticated user with access to some private pages
        When the queryset is retrieved
        Then only the pages the user has access to are returned
        """
        # Given
        rf = RequestFactory()
        url = "/api/v2/pages/"
        django_request = rf.get(url)

        request = Request(django_request)

        mock_user = mock.MagicMock()
        mock_user.permission_sets = MockPermissionSets(
            [{"theme": {"id": "1"}, "sub_theme": {"id": "-1"}}],
            has_global_access=False,
        )

        request.user = mock_user
        request.auth = "token"

        view = CMSPagesAPIViewSet()
        view.request = request

        # When
        result = view.get_queryset()

        # Then
        titles = [p.title for p in result]
        assert "Private Topic" in titles
        assert "Private Metric 2" in titles
        assert "Private Metric" not in titles


@pytest.mark.django_db
@mock.patch.dict(os.environ, {"CACHING_V2_ENABLED": "true"})
class TestCMSPagesAPI:
    path = "/api/pages/"

    @pytest.fixture
    def setup_pages(self):
        influenza_topic = Topic.objects.create(name="Search Influenza")
        metric = Metric.objects.create(
            name="search_influenza_headline_positivityLatest", topic=influenza_topic
        )

        covid_topic = Topic.objects.create(name="Search COVID-19")
        private_metric = Metric.objects.create(
            name="search_COVID-19_headline_cases_7DayTotals", topic=covid_topic
        )
        private_metric_two = Metric.objects.create(
            name="search_COVID-19_headline_7DayAdmissionsChange", topic=covid_topic
        )

        home = Page.objects.get(id=2)

        public_topic = TopicPage(
            title="Regression Search Public Topic",
            page_description="test",
            slug="regression-search-public-topic",
            is_public=True,
            theme="1",
            seo_title="regression-search-public-topic",
        )
        home.add_child(instance=public_topic)

        private_topic = TopicPage(
            title="Regression Search Private Topic",
            page_description="test",
            slug="regression-search-private-topic",
            is_public=False,
            theme="1",
            sub_theme="test",
            topic="test",
            page_classification="official_sensitive",
            seo_title="regression-search-private-topic",
        )
        home.add_child(instance=private_topic)

        public_metrics = MetricsDocumentationChildEntry(
            title="Regression Search Public Metric",
            page_description="test",
            slug="regression-search-public-metric",
            metric=metric.pk,
            is_public=True,
            seo_title="regression-search-public-metrics",
        )
        home.add_child(instance=public_metrics)

        private_metrics = MetricsDocumentationChildEntry(
            title="Regression Search Private Metric",
            page_description="test",
            slug="regression-search-private-metric",
            theme="2",
            sub_theme="test",
            topic="test",
            metric=private_metric.pk,
            is_public=False,
            seo_title="regression-search-private-metrics",
        )
        home.add_child(instance=private_metrics)

        private_metrics_two = MetricsDocumentationChildEntry(
            title="Regression Search Private Metric 2",
            page_description="test",
            slug="regression-search-private-metric-two",
            theme="1",
            sub_theme="test",
            topic="test",
            metric=private_metric_two.pk,
            is_public=False,
            seo_title="regression-search-private-metrics-two",
        )
        home.add_child(instance=private_metrics_two)

        standard_page = CommonPage(
            title="Regression Search Standard",
            body="test",
            slug="regression-search-standard",
            seo_title="regression-search-standard-page",
        )
        home.add_child(instance=standard_page)

    @staticmethod
    def _get_response_titles(response) -> set[str]:
        return {item["title"] for item in response.data["items"]}

    @mock.patch("cms.dashboard.viewsets.AUTH_ENABLED", True)
    def test_anonymous_search_returns_public_pages(self, setup_pages):
        """
        Given an unauthenticated request is made when auth is enabled
        When the list `GET /api/pages/?search=<term>` endpoint is hit
        Then an HTTP 200 OK response is returned with only public matching pages
        """
        # Given
        api_client = APIClient()

        # When
        response = api_client.get(
            path=self.path,
            data={"search": "Regression Search"},
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        titles = self._get_response_titles(response=response)
        assert "Regression Search Public Topic" in titles
        assert "Regression Search Public Metric" in titles
        assert "Regression Search Standard" in titles

        assert "Regression Search Private Topic" not in titles
        assert "Regression Search Private Metric" not in titles
        assert "Regression Search Private Metric 2" not in titles

    @mock.patch("cms.dashboard.viewsets.AUTH_ENABLED", False)
    def test_auth_disabled_returns_unfiltered_pages(self, setup_pages):
        """
        Given an unauthenticated request is made when auth is disabled
        When the list `GET /api/pages/` endpoint is hit
        Then an HTTP 200 OK response is returned with the unfiltered endpoints
        """
        # Given
        api_client = APIClient()

        # When
        response = api_client.get(path=self.path, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK

        titles = self._get_response_titles(response=response)
        assert "Regression Search Public Topic" in titles
        assert "Regression Search Public Metric" in titles
        assert "Regression Search Standard" in titles

        assert "Regression Search Private Topic" in titles
        assert "Regression Search Private Metric" in titles
        assert "Regression Search Private Metric 2" in titles

    @mock.patch("cms.dashboard.viewsets.AUTH_ENABLED", True)
    def test_restricted_user_search_returns_public_and_permitted_pages(
        self, setup_pages
    ):
        """
        Given an athenticated restricted user has access to some private pages
        When the list `GET /api/pages/?search=<term>` endpoint is hit
        Then an HTTP 200 OK response is returned with public and permitted matching pages
        """
        # Given
        mock_user = mock.MagicMock()
        mock_user.username = "restricted-user"
        mock_user.permission_sets = MockPermissionSets(
            [{"theme": {"id": "1"}, "sub_theme": {"id": "-1"}}], has_global_access=False
        )

        api_client = APIClient()
        api_client.force_authenticate(user=mock_user, token="token")

        # When
        response = api_client.get(
            path=self.path,
            data={"search": "Regression Search"},
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        titles = self._get_response_titles(response=response)
        assert "Regression Search Public Topic" in titles
        assert "Regression Search Public Metric" in titles
        assert "Regression Search Standard" in titles

        assert "Regression Search Private Topic" in titles
        assert "Regression Search Private Metric" not in titles
        assert "Regression Search Private Metric 2" in titles
