from cms.metrics_documentation.managers.parent import (
    MetricsDocumentationParentPageManager,
)
from cms.metrics_documentation.models import MetricsDocumentationParentPage
from tests.fakes.models.cms.metrics_documentation_parent import (
    FakeMetricsDocumentationParentPage,
)


class FakeMetricsDocumentationParentPageManager(MetricsDocumentationParentPageManager):
    """
    A fake version of the `MetricsDocumentationParentPageManager`
    which allows the methods and properties to be overriden
    to allow the database to be abstracted away.
    """

    def __init__(self, pages, **kwargs):
        self.pages = pages
        super().__init__(**kwargs)

    def get(self, slug: str) -> FakeMetricsDocumentationParentPage:
        try:
            return next(x for x in self.pages if x.slug == slug)
        except StopIteration:
            raise MetricsDocumentationParentPage.DoesNotExist
