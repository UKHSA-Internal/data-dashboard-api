from metrics.data.managers.core_models.stratum import StratumManager


class FakeStratumManager(StratumManager):
    """
    A fake version of the `StratumManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, strata, **kwargs):
        self.strata = strata
        super().__init__(**kwargs)

    def get_all_names(self) -> list[str]:
        return [stratum.name for stratum in self.strata]
