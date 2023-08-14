from metrics.data.managers.core_models.geography_type import GeographyTypeManager


class FakeGeographyTypeManager(GeographyTypeManager):
    """
    A fake version of the `GeographyTypeManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, geography_types, **kwargs):
        self.geography_types = geography_types
        super().__init__(**kwargs)

    def get_all_names(self) -> list[str]:
        return [geography_type.name for geography_type in self.geography_types]
