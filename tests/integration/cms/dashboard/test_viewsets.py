import pytest
from unittest.mock import MagicMock
from django.test import RequestFactory
from rest_framework.request import Request
from wagtail.models import Page

from cms.common.models import CommonPage
from cms.dashboard.viewsets import CMSPagesAPIViewSet
from cms.metrics_documentation.models.child import MetricsDocumentationChildEntry
from cms.topic.models import TopicPage
from metrics.data.models.core_models import Metric, Topic


@pytest.mark.django_db
class TestGetQuerySet:
    
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

        home = Page.objects.get(id=2)
        
        public_topic = TopicPage(title="Public Topic", page_description="test", slug="public-topic", is_public=True, theme="1", seo_title="public-topic")
        home.add_child(instance=public_topic)
        
        private_topic = TopicPage(title="Private Topic", page_description="test", slug="private-topic", is_public=False, theme="1", sub_theme="test", topic="test", page_classification="official_sensitive", seo_title="private-topic")
        home.add_child(instance=private_topic)
        
        public_metrics = MetricsDocumentationChildEntry(title="Public Metric", page_description="test", slug="public-metric", metric=metric.pk, is_public=True, seo_title="public-metrics")
        home.add_child(instance=public_metrics)

        private_metrics = MetricsDocumentationChildEntry(title="Private Metric", page_description="test", slug="private-metric", theme="2", sub_theme="test", topic="test", metric=private_metric.pk, is_public=False, seo_title="private-metrics")
        home.add_child(instance=private_metrics)
        
        standard_page = CommonPage(title="Standard", body="test", slug="standard", seo_title="standard-page")
        home.add_child(instance=standard_page)
        
        return {
            "public_topic": public_topic,
            "private_topic": private_topic,
            "public_metrics": public_metrics,
            "private_metrics": private_metrics,
            "standard_page": standard_page
        }

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

        mock_user = MagicMock()
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

        mock_user = MagicMock()
        mock_user.permission_sets = {
            "has_global_access": True,
            "permission_set_hierarchy": []
        }

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

        mock_user = MagicMock()
        mock_user.permission_sets = {
            "has_global_access": False,
            "permission_set_hierarchy": [{"theme": {"id": "1"}, "sub_theme": {"id": "-1"}}]
        }

        request.user = mock_user
        request.auth = "token"

        view = CMSPagesAPIViewSet()
        view.request = request

        # When
        result = view.get_queryset()
        
        # Then
        titles = [p.title for p in result]
        assert "Private Topic" in titles
        assert "Private Metrics" not in titles
