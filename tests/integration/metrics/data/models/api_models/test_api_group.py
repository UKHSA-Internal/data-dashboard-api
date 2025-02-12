import pytest
from metrics.data.models.api_models.api_groups import ApiGroup
from metrics.data.models.api_models.api_permissions import ApiPermission
from metrics.data.models.core_models import (
    Theme,
    SubTheme,
    Topic,
    Metric,
)


class TestApiGroup:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.theme = Theme.objects.create(name="infectious_disease")
        self.sub_theme = SubTheme.objects.create(name="respiratory", theme=self.theme)
        self.topic1 = Topic.objects.create(name="COVID-19", sub_theme=self.sub_theme)
        self.topic2 = Topic.objects.create(name="asthma", sub_theme=self.sub_theme)
        self.metric1 = Metric.objects.create(
            name="asthma_syndromic_emergencyDepartment_countsByDay"
        )
        self.metric2 = Metric.objects.create(name="COVID-19_cases_rateRollingMean")

        self.api_group = ApiGroup.objects.create(name="admin_group")
        self.permission1 = ApiPermission.objects.create(
            name="permission1",
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic1,
            metric=self.metric1,
        )
        self.permission2 = ApiPermission.objects.create(
            name="permission2",
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic2,
            metric=self.metric2,
        )

    @pytest.mark.django_db
    def test_create_api_group(self):
        assert ApiGroup.objects.count() == 1
        assert self.api_group.name == "admin_group"

    @pytest.mark.django_db
    def test_api_group_str(self):
        assert str(self.api_group) == "admin_group"

    @pytest.mark.django_db
    def test_add_permissions_to_api_group(self):
        self.api_group.permissions.add(self.permission1, self.permission2)
        assert self.api_group.permissions.count() == 2

    @pytest.mark.django_db
    def test_remove_permission_from_api_group(self):
        self.api_group.permissions.add(self.permission1)
        self.api_group.permissions.remove(self.permission1)
        assert self.api_group.permissions.count() == 0

    @pytest.mark.django_db
    def test_unique_api_group_name(self):
        with pytest.raises(Exception):
            ApiGroup.objects.create(name="admin_group")
