from metrics.data.managers.core_models.geography import GeographyManager


class FakeGeographyManager(GeographyManager):
    """
    A fake version of the `GeographyManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, geographies, **kwargs):
        self.geographies = geographies
        super().__init__(**kwargs)

    def get_all_names(self) -> list[str]:
        return list({geography.name for geography in self.geographies})
