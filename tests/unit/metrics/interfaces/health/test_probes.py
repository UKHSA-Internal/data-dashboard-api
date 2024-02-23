from unittest import mock

import pytest
import redis

from metrics.api import enums
from metrics.interfaces.health.probes import (
    HealthProbeForCacheFailedError,
    HealthProbeForDatabaseFailedError,
    HealthProbeManagement,
)

MODULE_PATH = "metrics.interfaces.health.probes"


class TestHealthProbeManagement:
    # Tests for the `__init__()` method
    @mock.patch(f"{MODULE_PATH}.django_db_proxy")
    def test_uses_django_db_connection_proxy_if_not_provided(
        self, spy_django_db_proxy: mock.MagicMock
    ):
        """
        Given an instance of `HealthProbeManagement`
        When the object is initialized
        Then the django db connection proxy
            is given by default to the `_database_connection` attribute

        Patches:
            `spy_django_db_connection`: For the main assertion
                to check that the Django db connection proxy
                is given to the `__init__()` method if not
                explicitly provided
        """
        # Given / When
        health_probe_management = HealthProbeManagement(
            cache_connection=mock.Mock(),
        )

        # Then
        assert health_probe_management._database_connection == spy_django_db_proxy

    @mock.patch(f"{MODULE_PATH}.django_cache_proxy")
    def test_uses_django_cache_connection_proxy_if_not_provided(
        self, spy_django_cache_proxy: mock.MagicMock
    ):
        """
        Given an instance of `HealthProbeManagement`
        When the object is initialized
        Then the django cache connection proxy is processed and
            is given by default to the `_cache_connection` attribute

        Patches:
            `spy_django_db_connection`: For the main assertion
                to check that the Django cache connection proxy
                is given to the `__init__()` method if not
                explicitly provided
        """
        # Given / When
        health_probe_management = HealthProbeManagement()

        # Then
        expected_cache_client = spy_django_cache_proxy._cache.get_client.return_value
        assert health_probe_management._cache_connection == expected_cache_client

    # Tests for the main entrypoint health probe

    @mock.patch.object(HealthProbeManagement, "ping_cache")
    @mock.patch.object(HealthProbeManagement, "ping_database")
    @pytest.mark.parametrize(
        "current_app_mode, db_ping_count, cache_ping_count",
        (
            [enums.AppMode.PRIVATE_API.value, 1, 1],
            [enums.AppMode.PUBLIC_API.value, 1, 0],
            [enums.AppMode.CMS_ADMIN.value, 1, 0],
            [enums.AppMode.INGESTION.value, 1, 0],
            [enums.AppMode.FEEDBACK_API.value, 0, 0],
        ),
    )
    def test_perform_health_pings_dependant_services_according_to_app_mode(
        self,
        spy_ping_database: mock.MagicMock,
        spy_cache_database: mock.MagicMock,
        current_app_mode: str,
        db_ping_count: int,
        cache_ping_count: int,
        monkeypatch,
    ):
        """
        Given the `APP_MODE` env var is set to valid value
        When `perform_health_check()` is called
            from an instance of `HealthProbeManagement`
        Then the dependant pings are performed
            according to what is required by the selected app mode

        Patches:
            `spy_ping_database`: To check if the db was pinged
            `spy_ping_cache`: To check if the cache was pinged

        """
        # Given
        monkeypatch.setenv(name="APP_MODE", value=current_app_mode)
        health_probe_management = HealthProbeManagement(
            database_connection=mock.Mock(),
            cache_connection=mock.Mock(),
        )

        # When
        health_probe_management.perform_health_check()

        # Then
        assert spy_ping_database.call_count == db_ping_count
        assert spy_cache_database.call_count == cache_ping_count

    @pytest.mark.parametrize(
        "current_app_mode, db_ping_is_healthy, cache_ping_is_healthy",
        (
            # The `PRIVATE_API` needs both the db and cache to be healthy at once
            [enums.AppMode.PRIVATE_API.value, True, True],
            # The `PUBLIC_API` only needs the db, the cache is irrelevant
            [enums.AppMode.PUBLIC_API.value, True, True],
            [enums.AppMode.PUBLIC_API.value, True, False],
            # The `CMS_ADMIN` only needs the db, the cache is irrelevant
            [enums.AppMode.CMS_ADMIN.value, True, True],
            [enums.AppMode.CMS_ADMIN.value, True, False],
            # The `INGESTION` only needs the db, the cache is irrelevant
            [enums.AppMode.INGESTION.value, True, True],
            [enums.AppMode.INGESTION.value, True, False],
            # The `FEEDBACK_API` does not need the db or the cache
            [enums.AppMode.FEEDBACK_API.value, True, True],
            [enums.AppMode.FEEDBACK_API.value, True, False],
            [enums.AppMode.FEEDBACK_API.value, False, False],
        ),
    )
    def test_returns_true_if_relevant_probes_are_healthy_for_selected_app_mode(
        self,
        current_app_mode: str,
        db_ping_is_healthy: bool,
        cache_ping_is_healthy: bool,
        monkeypatch,
    ):
        """
        Given a valid `APP_MODE` env var
        And the relevant probes are healthy
        When `perform_health_check()` is called
            from an instance of `HealthProbeManagement`
        Then True is returned
        """
        # Given
        monkeypatch.setenv(name="APP_MODE", value=current_app_mode)

        mocked_db_connection = mock.Mock()
        mocked_db_connection.is_usable.return_value = db_ping_is_healthy
        mocked_cache_connection = mock.Mock()
        mocked_cache_connection.ping.return_value = cache_ping_is_healthy
        health_probe_management = HealthProbeManagement(
            cache_connection=mocked_cache_connection,
            database_connection=mocked_db_connection,
        )

        # When
        is_healthy: bool = health_probe_management.perform_health_check()

        # Then
        assert is_healthy

    @pytest.mark.parametrize(
        "current_app_mode, db_ping_is_healthy, cache_ping_is_healthy",
        (
            # The `PRIVATE_API` needs both the db and cache to be healthy at once
            [enums.AppMode.PRIVATE_API.value, False, True],
            [enums.AppMode.PRIVATE_API.value, True, False],
            [enums.AppMode.PRIVATE_API.value, False, False],
            # The `PUBLIC_API` always needs the db, the cache is irrelevant
            [enums.AppMode.PUBLIC_API.value, False, True],
            [enums.AppMode.PUBLIC_API.value, False, False],
            # The `CMS_ADMIN` always needs the db, the cache is irrelevant
            [enums.AppMode.CMS_ADMIN.value, False, True],
            [enums.AppMode.CMS_ADMIN.value, False, False],
            # The `INGESTION` only needs the db, the cache is irrelevant
            [enums.AppMode.INGESTION.value, False, True],
            [enums.AppMode.INGESTION.value, False, False],
            # The `FEEDBACK_API` does not need the db or the cache
            # and as such will not return an unhealthy ping so is omitted
        ),
    )
    def test_returns_false_if_relevant_probes_are_unhealthy_for_selected_app_mode(
        self,
        current_app_mode: str,
        db_ping_is_healthy: bool,
        cache_ping_is_healthy: bool,
        monkeypatch,
    ):
        """
        Given a valid `APP_MODE` env var
        And the relevant probes are unhealthy
        When `perform_health_check()` is called
            from an instance of `HealthProbeManagement`
        Then False is returned
        """
        # Given
        monkeypatch.setenv(name="APP_MODE", value=current_app_mode)

        mocked_db_connection = mock.Mock()
        mocked_db_connection.is_usable.return_value = db_ping_is_healthy
        mocked_cache_connection = mock.Mock()
        mocked_cache_connection.ping.return_value = cache_ping_is_healthy
        health_probe_management = HealthProbeManagement(
            cache_connection=mocked_cache_connection,
            database_connection=mocked_db_connection,
        )

        # When
        is_healthy: bool = health_probe_management.perform_health_check()

        # Then
        assert not is_healthy

    # Tests for the cache probe

    def test_ping_cache_returns_true_if_ping_returns_healthy_true(self):
        """
        Given a cache connection
            which returns True from the `ping()` method
        When `ping_cache()` is called from
            an instance of `HealthProbeManagement`
        Then None is returned and no error is raised
        """
        # Given
        mocked_cache_connection = mock.Mock()
        mocked_cache_connection.ping.return_value = True
        health_probe_management = HealthProbeManagement(
            cache_connection=mocked_cache_connection
        )

        # When
        cache_ping = health_probe_management.ping_cache()

        # Then
        assert cache_ping is None

    def test_ping_cache_raises_error_if_ping_returns_unhealthy_false(self):
        """
        Given a cache connection
            which returns False from the `ping()` method
        When `ping_cache()` is called from
            an instance of `HealthProbeManagement`
        Then a `HealthProbeForCacheFailedError` is raised
        """
        # Given
        mocked_cache_connection = mock.Mock()
        mocked_cache_connection.ping.return_value = False
        health_probe_management = HealthProbeManagement(
            cache_connection=mocked_cache_connection
        )

        # When / Then
        with pytest.raises(HealthProbeForCacheFailedError):
            health_probe_management.ping_cache()

    @pytest.mark.parametrize(
        "exception",
        (
            [
                redis.ConnectionError,
                redis.AuthenticationError,
                redis.TimeoutError,
                redis.OutOfMemoryError,
                redis.BusyLoadingError,
                redis.ResponseError,
            ]
        ),
    )
    def test_ping_cache_raises_error_if_ping_throws_error(self, exception: Exception):
        """
        Given a cache connection
            which raises an error from the `ping()` method
        When `ping_cache()` is called from
            an instance of `HealthProbeManagement`
        Then a `HealthProbeForCacheFailedError` is raised
        """
        # Given
        mocked_cache_connection = mock.Mock()
        mocked_cache_connection.ping.side_effect = exception
        health_probe_management = HealthProbeManagement(
            cache_connection=mocked_cache_connection
        )

        # When / Then
        with pytest.raises(HealthProbeForCacheFailedError):
            health_probe_management.ping_cache()

    # Tests for the database probe

    def test_ping_database_does_not_raise_error_if_healthy(self):
        """
        Given a database connection
            which returns True from the `is_useable()` method
        When `ping_database()` is called from
            an instance of `HealthProbeManagement`
        Then None is returned and no error is raised
        """
        # Given
        mocked_database_connection = mock.Mock()
        mocked_database_connection.is_usable.return_value = True
        health_probe_management = HealthProbeManagement(
            cache_connection=mock.Mock(), database_connection=mocked_database_connection
        )

        # When
        db_ping = health_probe_management.ping_database()

        # Then
        assert db_ping is None

    def test_ping_database_raises_error_if_unhealthy(self):
        """
        Given a database connection
            which returns False from the `is_useable()` method
        When `ping_database()` is called from
            an instance of `HealthProbeManagement`
        Then a `HealthProbeForDatabaseFailedError` is raised
        """
        # Given
        mocked_database_connection = mock.Mock()
        mocked_database_connection.is_usable.return_value = False
        health_probe_management = HealthProbeManagement(
            cache_connection=mock.Mock(), database_connection=mocked_database_connection
        )

        # When / Then
        with pytest.raises(HealthProbeForDatabaseFailedError):
            health_probe_management.ping_database()
