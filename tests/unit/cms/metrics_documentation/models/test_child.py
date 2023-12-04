from unittest import mock

import pytest

from cms.metrics_documentation.models.child import MetricsDocumentationChildEntry
from tests.fake.models.queryset import FakeQuerySet


class TestMetricsDocumentationChildEntryPage:
    @pytest.mark.parametrize(
       "expected_api_fields",
       [
           "date_posted",
           "body",
           "metric_name",
           "last_published_date",
           "seo_title",
           "search_description",
       ],
    )
    def test_has_correct_api_fields(
       self,
       expected_api_fields: str,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When `api_fields` is called.
        Then the expected names are on the returend `APIField` objects.
        """
