import factory

from cms.dashboard.management.commands.build_cms_site import open_example_page_response
from tests.fakes.models.cms.metrics_documentation_child import (
    FakeMetricsDocumentationChildEntry,
)


class FakeMetricsDocumentationChildEntryFactory(factory.Factory):
    """
    Factory for creating `MetricsDocumentationChildEntry` instances for tests
    """

    class Meta:
        model = FakeMetricsDocumentationChildEntry

    @classmethod
    def build_page_from_template(cls, **kwargs):
        data = open_example_page_response(
            page_name="metrics_documentation_covid-19_deaths_onsbyweek"
        )
        return cls.build(
            title=data["title"], body=data["body"], slug=data["meta"]["slug"], **kwargs
        )
