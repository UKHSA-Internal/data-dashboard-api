import contextlib
import datetime
from typing import List, Dict

import factory
from metrics.api.models import (
    ApiPermission,
    ApiGroup,
)


from django.utils import timezone


class ApiGroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ApiGroup

    @classmethod
    def create_record(
            cls,
            name: str = "default",
            permissions: List[ApiPermission] = [],
            **kwargs,
    ):

        group = cls.create(name=name, **kwargs)
        # Fetch or create permissions and add them to the group
        for permission in permissions:
            group.permissions.add(permission)
        return group

    @classmethod
    def _make_datetime_timezone_aware(
            cls, datetime_obj: str | datetime.datetime | None
    ) -> datetime.datetime:

        if datetime_obj is None:
            return datetime_obj

        with contextlib.suppress(TypeError):
            # If it is already a datetime object then suppress the resulting TypeError
            datetime_obj = datetime.datetime.strptime(datetime_obj, "%Y-%m-%d")

        try:
            return timezone.make_aware(value=datetime_obj)
        except ValueError:
            # The object is already timezone aware
            return datetime_obj
