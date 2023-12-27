import operator

from django.db.models import QuerySet


class FakeQuerySet(QuerySet):
    """
    A fake version of the `Queryset` which allows methods and properties
    to be overridden in order to provide decoupling for tests
    and emulation of `QuerySet` behaviour
    """

    def __init__(self, instances: list = None, **kwargs):
        self.fake_instances = instances or []
        self.latest_date = None
        super().__init__(**kwargs)

    def __iter__(self):
        yield from self.fake_instances

    def __getitem__(self, k):
        return self.fake_instances[k]

    def _fetch_all(self):
        return self.fake_instances

    def count(self) -> int:
        return len(self.fake_instances)

    def values_list(self, *fields, **kwargs):
        fields_as_dotted_paths = [f.replace("__", ".") for f in fields]

        return [
            tuple(
                operator.attrgetter(field)(fake_instance)
                for field in fields_as_dotted_paths
            )
            for fake_instance in self.fake_instances
        ]

    def exists(self) -> bool:
        return bool(self.fake_instances)
