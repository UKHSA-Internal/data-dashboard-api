import factory

from metrics.data.models.core_models import Geography, GeographyType


class GeographyFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Geography` instances for tests
    """

    class Meta:
        model = Geography

    @classmethod
    def create_with_geography_type(
        cls, name: str, geography_code: str, geography_type: str
    ):
        geography_type, _ = GeographyType.objects.get_or_create(name=geography_type)

        return cls.create(
            name=name,
            geography_code=geography_code,
            geography_type=geography_type,
        )
