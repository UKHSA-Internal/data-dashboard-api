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

    def get_geography_codes_and_names_by_geography_type(
        self,
        geography_type_name: str,
    ):
        return self.geographies

    def does_geography_code_exist(
        self, geography_code: str, geography_type_name
    ) -> str:
        for code, name in self.get_geography_codes_and_names_by_geography_type(
            geography_type_name=geography_type_name
        ):
            if code == geography_code:
                return True

            return False
