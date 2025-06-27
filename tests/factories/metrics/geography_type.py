import factory

from metrics.data.models.core_models import Geography, GeographyType


class GeographyTypeFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `GeographyType` instances for tests
    """

    class Meta:
        model = GeographyType

    @factory.post_generation
    def with_geographies(self, create, extracted, **kwargs):
        if create:
            geography_names: list[str] = extracted

            geographies = [
                Geography.objects.create(name=geography_name)
                for geography_name in geography_names
            ]
            for geography in geographies:
                geography.geography_type = self
                geography.save(update_fields=["geography_type"])
