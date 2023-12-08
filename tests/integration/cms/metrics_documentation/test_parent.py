import pytest
from django.core.exceptions import ValidationError

from cms.metrics_documentation.models import MetricsDocumentationParentPage


class TestMetricsDocumentationParentPage:
    @pytest.mark.django_db
    def test_there_can_only_be_one_live_page(self):
        """
        Given 1 Metrics documentation parent page exists and is published.
        When A second parent page is published.
        Then A `ValidationError` is raised.
        """
        # Given
        MetricsDocumentationParentPage.objects.create(
            path="abc",
            depth=1,
            title="first parent page",
            slug="metrics-documentation",
            date_posted="2023-11-01",
            body="lorem ipsum...",
            live=True,
        )

        # When / Then
        with pytest.raises(ValidationError):
            MetricsDocumentationParentPage.objects.create(
                path="def",
                depth=1,
                title="second parent page",
                slug="metrics-documentation",
                date_posted="2023-11-02",
                body="lorem ipsum...",
                live=True,
            )
