from cms.metrics_documentation.models import MetricsDocumentationParentPage
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeMetricsDocumentationParentPage(MetricsDocumentationParentPage):
    """
    A fake version of the Django model `MetricsDocumentationParentPage`
    which has had its dependencies altered so that it does not interact with the database.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `MetricsDocumentationParentPage` model.
        """
        super().__init__(content_type_id=1, **kwargs)
