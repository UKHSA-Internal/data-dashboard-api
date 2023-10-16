from django.db.models import QuerySet


class FakeQuerySet(QuerySet):
    """
    A fake version of the `Queryset` which allows methods and properties
    to be overridden in order to provide decoupling for tests
    and emulation of `QuerySet` behaviour
    """

    def __init__(self, instances: list = None, **kwargs):
        self.fake_instances = instances or []
        self.latest_refresh_date = None
        super().__init__(**kwargs)

    def __iter__(self):
        yield from self.fake_instances

    def __getitem__(self, k):
        return self.fake_instances[k]

    def _fetch_all(self):
        return self.fake_instances
