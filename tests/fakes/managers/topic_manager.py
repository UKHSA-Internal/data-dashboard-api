from metrics.data.managers.core_models.topic import TopicManager
from tests.fakes.models.metrics.topic import FakeTopic


class FakeTopicManager(TopicManager):
    """
    A fake version of the `TopicManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, topics, **kwargs):
        self.topics = topics
        super().__init__(**kwargs)

    def get_by_name(self, name: str):
        try:
            return next(x for x in self.topics if x.name == name)
        except StopIteration as error:
            raise FakeTopic.DoesNotExist from error

    def get_all_names(self) -> list[str]:
        return [topic.name for topic in self.topics]

    def does_topic_exist(self, topic: str) -> bool:
        return topic in self.get_all_names()
