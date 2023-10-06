from metrics.data.managers.core_models.headline import CoreHeadlineManager


class FakeCoreHeadlineManager(CoreHeadlineManager):
    """
    A fake version of the `CoreHeadlineManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, headlines, **kwargs):
        self.headlines = headlines
        super().__init__(**kwargs)

    def get_latest_metric_value(
        self,
        topic_name: str,
        metric_name: str,
        geography_name: str | None = None,
        geography_type_name: str | None = None,
        stratum_name: str | None = None,
        sex: str | None = None,
        age: str | None = None,
    ) -> float | None:
        filtered_headlines = [
            core_headline
            for core_headline in self.headlines
            if core_headline.metric.metric_group.topic.name == topic_name
            if core_headline.metric.name == metric_name
        ]

        if geography_name:
            filtered_headlines = [
                x for x in filtered_headlines if x.geography.name == geography_name
            ]

        if geography_type_name:
            filtered_headlines = [
                x
                for x in filtered_headlines
                if x.geography.geography_type.name == geography_type_name
            ]

        if stratum_name:
            filtered_headlines = [
                x for x in filtered_headlines if x.stratum.name == stratum_name
            ]

        if sex:
            filtered_headlines = [x for x in filtered_headlines if x.sex == sex]

        if age:
            filtered_headlines = [x for x in filtered_headlines if x.age.name == age]

        try:
            return filtered_headlines[0].metric_value
        except IndexError:
            return None
