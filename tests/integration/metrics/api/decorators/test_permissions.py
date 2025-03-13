import pytest
import copy
from typing import Any, Callable
from unittest.mock import MagicMock

from django.core.serializers.base import Serializer

from metrics.api.decorators import (
    filter_by_permissions,
)
from tests.factories.metrics.time_series import CoreTimeSeriesFactory
from metrics.data.models.rbac_models import RBACPermission
from metrics.data.models.core_models import (
    Theme,
    SubTheme,
    Topic,
)

MODULE_PATH = "metrics.api.settings.private_api"

core_headline_data = {
    "theme": "infectious_disease",
    "sub_theme": "respiratory",
    "topic": "COVID-19",
    "metric": "COVID-19_cases_casesByDay",
    "geography": "England",
    "geography_type": "Nation",
    "sex": "all",
    "age": "all",
    "stratum": "default",
    "metric_value": 123.45,
    "period_start": "2024-01-01 00:00:00",
    "period_end": "2024-02-02 00:00:00",
    "is_public": True,
}


class FakeSerializer:
    def __init__(self, *args, **kwargs):
        self.context = kwargs.get("context", {})

    def to_representation(self, instance):
        return instance


@pytest.fixture
def mock_request():
    mock_req = MagicMock()
    mock_req.group_permissions = [MagicMock()]
    return mock_req


@pytest.fixture
def fake_serializer(mock_request):
    @filter_by_permissions()
    class WrappedSerializer(FakeSerializer):
        pass

    return WrappedSerializer(context={"request": mock_request})


class TestPermissions:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Theme
        self.non_communicable = Theme.objects.create(name="non-communicable")

        # Subtheme
        self.respiratory_comm = SubTheme.objects.create(
            name="respiratory", theme=self.non_communicable
        )

        # Topic
        self.asthma = Topic.objects.create(
            name="asthma", sub_theme=self.respiratory_comm
        )

        # CoreTimeSeries
        self.core_covid_19 = CoreTimeSeriesFactory.create_record()

        self.core_asthma = CoreTimeSeriesFactory.create_record(
            theme_name=self.non_communicable.name,
            sub_theme_name=self.respiratory_comm.name,
            topic_name=self.asthma.name,
            metric_name="COVID-19_cases_casesByDay2",
        )

        self.non_communicable_permission = RBACPermission.objects.create(
            name="medical",
            theme=self.non_communicable,
            sub_theme=self.respiratory_comm,
        )

    @pytest.mark.django_db
    def test_filter_by_permissions_non_private_api(
        self: Any,
        patch_auth_disabled: Callable[[], None],  # Sets AUTH_ENABLED "0"
        fake_serializer: Serializer,
    ):
        """
        Given `AUTH_ENABLED` is disabled
        When `to_representation()` is called on the serializer
        Then the `is_public` field is removed and all other fields are returned
        """
        # Given
        serializer = fake_serializer

        # When
        result = serializer.to_representation(core_headline_data)

        # Then
        assert "is_public" not in result, "is_public should be removed"
        assert result == core_headline_data, "all fields should be returned"

    @pytest.mark.parametrize(
        "theme,sub_theme",
        [
            ("infectious_disease", "respiratory"),
            ("non-communicable", "respiratory"),
        ],
    )
    @pytest.mark.django_db
    def test_filter_by_permissions_theme_sub_theme(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
        theme: str,
        sub_theme: str,
    ):
        """
        Given authentication is enabled
        And the user has matching RBAC permissions for theme & sub_theme
        When `to_representation()` is called on the serializer
        Then only the data matching the user’s permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["theme"] = theme
        test_data_public["sub_theme"] = sub_theme
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.parametrize(
        "theme,sub_theme",
        [
            ("infectious_disease", "vaccine_preventable"),
            ("non-communicable", "respiratory_other"),
        ],
    )
    @pytest.mark.django_db
    def test_filter_by_permissions_excludes_non_matching_theme_sub_theme(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
        theme: str,
        sub_theme: str,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions, but they do not match the provided theme & sub_theme
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["theme"] = theme
        test_data_public["sub_theme"] = sub_theme
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result is None

    @pytest.mark.parametrize(
        "theme,sub_theme,topic",
        [
            ("infectious_disease", "respiratory", "COVID-19"),
            ("non-communicable", "respiratory", "COVID-19"),
        ],
    )
    @pytest.mark.django_db
    def test_filter_by_permissions_topic(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
        theme: str,
        sub_theme: str,
        topic: str,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific topic
        When `to_representation()` is called on the serializer
        Then only the data matching the user's topic permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["theme"] = theme
        test_data_public["sub_theme"] = sub_theme
        test_data_public["topic"] = topic
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.parametrize(
        "theme,sub_theme,topic",
        [
            ("infectious_disease", "vaccine_preventable", "Measles"),
            ("non-communicable", "respiratory_other", "COVID-19"),
        ],
    )
    @pytest.mark.django_db
    def test_filter_by_permissions_topic_without_correct_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
        theme: str,
        sub_theme: str,
        topic: str,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific topic
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["theme"] = theme
        test_data_public["sub_theme"] = sub_theme
        test_data_public["topic"] = topic
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result is None

    @pytest.mark.parametrize(
        "theme,sub_theme,topic,metric",
        [
            (
                "infectious_disease",
                "respiratory",
                "COVID-19",
                "COVID-19_cases_casesByDay",
            ),
            (
                "non-communicable",
                "respiratory",
                "COVID-19",
                "COVID-19_cases_casesByDay",
            ),
        ],
    )
    @pytest.mark.django_db
    def test_filter_by_permissions_metric(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific metric
        When `to_representation()` is called on the serializer
        Then only the data matching the user's metric permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["theme"] = theme
        test_data_public["sub_theme"] = sub_theme
        test_data_public["topic"] = topic
        test_data_public["metric"] = metric
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.parametrize(
        "theme,sub_theme,topic,metric",
        [
            (
                "infectious_disease",
                "respiratory",
                "COVID-19",
                "COVID-20_cases_casesByDay2",
            ),
            (
                "non-communicable",
                "respiratory_other",
                "COVID-19",
                "COVID-19_cases_casesByDay",
            ),
        ],
    )
    @pytest.mark.django_db
    def test_filter_by_permissions_metric_with_no_matching_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
        theme: str,
        sub_theme: str,
        topic: str,
        metric: str,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific metric
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["theme"] = theme
        test_data_public["sub_theme"] = sub_theme
        test_data_public["topic"] = topic
        test_data_public["metric"] = metric
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == None

    @pytest.mark.django_db
    def test_filter_by_permissions_geography(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific geography
        When `to_representation()` is called on the serializer
        Then only the data matching the user's geography permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["geography"] = "England"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.django_db
    def test_filter_by_permissions_geography_with_non_matching_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific geography
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["geography"] = "Scotland"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result is None

    @pytest.mark.django_db
    def test_filter_by_permissions_geography_type(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific geography type
        When `to_representation()` is called on the serializer
        Then only the data matching the user's geography type permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
            geography_type=self.core_covid_19.geography.geography_type,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["geography_type"] = "Nation"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.django_db
    def test_filter_by_permissions_geography_type_with_non_matching_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific geography type
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
            geography_type=self.core_covid_19.geography.geography_type,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["geography_type"] = "Local"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result is None

    @pytest.mark.django_db
    def test_filter_by_permissions_age(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific age group
        When `to_representation()` is called on the serializer
        Then only the data matching the user's age permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
            geography_type=self.core_covid_19.geography.geography_type,
            age=self.core_covid_19.age,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["age"] = "all"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.django_db
    def test_filter_by_permissions_age_with_no_matching_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific age group
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
            geography_type=self.core_covid_19.geography.geography_type,
            age=self.core_covid_19.age,
        )
        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["age"] = "01-04"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result is None

    @pytest.mark.django_db
    def test_filter_by_permissions_age(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific stratum
        When `to_representation()` is called on the serializer
        Then only the data matching the user's stratum permissions is returned
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
            geography_type=self.core_covid_19.geography.geography_type,
            age=self.core_covid_19.age,
            stratum=self.core_covid_19.stratum,
        )

        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["stratum"] = "default"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result == test_data_public
        assert "is_public" not in result

    @pytest.mark.django_db
    def test_filter_by_permissions_age_with_not_matching_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given authentication is enabled
        And the user has RBAC permissions for a specific stratum
        When `to_representation()` is called on the serializer
        Then the result should be None, as no data matches the user’s permissions
        """
        # Given
        infectious_disease_permission = RBACPermission.objects.create(
            name="infectious_disease_permission",
            theme=self.core_covid_19.metric.topic.sub_theme.theme,
            sub_theme=self.core_covid_19.metric.topic.sub_theme,
            topic=self.core_covid_19.metric.topic,
            metric=self.core_covid_19.metric,
            geography=self.core_covid_19.geography,
            geography_type=self.core_covid_19.geography.geography_type,
            age=self.core_covid_19.age,
            stratum=self.core_covid_19.stratum,
        )

        serializer = fake_serializer

        test_data_public = copy.deepcopy(core_headline_data)
        test_data_public["stratum"] = "other"
        test_data_public["is_public"] = False

        mock_request = MagicMock()
        mock_request.group_permissions = [
            infectious_disease_permission,
            self.non_communicable_permission,
        ]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data_public)

        # Then
        assert result is None

    @pytest.mark.django_db
    def test_filter_by_permissions_returns_none_if_no_permissions(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given `request.group_permissions` is empty
        When `to_representation()` is called on the serializer
        Then it should return None
        """
        # Given
        serializer = fake_serializer
        test_data = copy.deepcopy(core_headline_data)
        test_data["is_public"] = False  # Ensure private data

        # Simulate an empty group_permissions list
        mock_request = MagicMock()
        mock_request.group_permissions = []  # No permissions available
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data)

        # Then
        assert result is None

    @pytest.mark.django_db
    def test_filter_by_permissions_removes_is_public_if_true(
        self: Any,
        patch_auth_enabled: Callable[[], None],  # Sets AUTH_ENABLED "1"
        fake_serializer: Serializer,
    ):
        """
        Given an instance where `is_public` is set to True
        When `to_representation()` is called on the serializer
        Then it should return the original data with `is_public` removed
        """

        # Given
        serializer = fake_serializer
        test_data = copy.deepcopy(core_headline_data)
        test_data["is_public"] = True

        mock_request = MagicMock()
        mock_request.group_permissions = [MagicMock()]
        serializer.context = {"request": mock_request}

        # When
        result = serializer.to_representation(test_data)

        # Then
        assert result is not None
        assert "is_public" not in result
