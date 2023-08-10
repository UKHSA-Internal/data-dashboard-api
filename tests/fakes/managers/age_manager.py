from metrics.data.managers.core_models.age import AgeManager


class FakeAgeManager(AgeManager):
    """
    A fake version of the `AgeManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, ages, **kwargs):
        self.ages = ages
        super().__init__(**kwargs)

    def get_all_names(self) -> list[str]:
        return [age.name for age in self.ages]
