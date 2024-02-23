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
            `spy_django_cache_proxy`: For the main assertion
                to check that the Django cache connection proxy
                is given to the `__init__()` method if not
                explicitly provided
        """
        # Given / When
        health_probe_management = HealthProbeManagement()

        # Then
        assert health_probe_management._cache_connection == spy_django_cache_proxy

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

    @mock.patch.object(HealthProbeManagement, "ping_database")
    @mock.patch.object(HealthProbeManagement, "ping_cache")
    @pytest.mark.parametrize(
        "current_app_mode, db_ping_thrown_error, cache_ping_thrown_error",
        (
            # The `PRIVATE_API` needs both the db and cache to be healthy at once
            [enums.AppMode.PRIVATE_API.value, None, None],
            # The `PUBLIC_API` only needs the db, the cache is irrelevant
            [enums.AppMode.PUBLIC_API.value, None, None],
            [enums.AppMode.PUBLIC_API.value, None, HealthProbeForCacheFailedError],
            # The `CMS_ADMIN` only needs the db, the cache is irrelevant
            [enums.AppMode.CMS_ADMIN.value, None, None],
            [enums.AppMode.CMS_ADMIN.value, None, HealthProbeForCacheFailedError],
            # The `INGESTION` only needs the db, the cache is irrelevant
            [enums.AppMode.INGESTION.value, None, None],
            [enums.AppMode.INGESTION.value, None, HealthProbeForCacheFailedError],
            # The `FEEDBACK_API` does not need the db or the cache
            [enums.AppMode.FEEDBACK_API.value, None, None],
            [enums.AppMode.FEEDBACK_API.value, None, HealthProbeForCacheFailedError],
            [
                enums.AppMode.FEEDBACK_API.value,
                HealthProbeForCacheFailedError,
                HealthProbeForCacheFailedError,
            ],
        ),
    )
    def test_returns_true_if_relevant_probes_are_healthy_for_selected_app_mode(
        self,
        mocked_ping_cache: mock.MagicMock,
        mocked_ping_database: mock.MagicMock,
        current_app_mode: str,
        db_ping_thrown_error: HealthProbeForDatabaseFailedError | None,
        cache_ping_thrown_error: HealthProbeForCacheFailedError | None,
        monkeypatch,
    ):
        """
        Given a valid `APP_MODE` env var
        And the relevant probes are healthy
        When `perform_health_check()` is called
            from an instance of `HealthProbeManagement`
        Then True is returned

        Patches:
            `mocked_ping_cache`: To simulate the
                result of the ping being made to the cache
            `mocked_ping_database`: To simulate the
                result of the ping being made to the db

        """
        # Given
        monkeypatch.setenv(name="APP_MODE", value=current_app_mode)
        mocked_ping_database.side_effect = db_ping_thrown_error
        mocked_ping_cache.side_effect = cache_ping_thrown_error

        health_probe_management = HealthProbeManagement()

        # When
        is_healthy: bool = health_probe_management.perform_health_check()

        # Then
        assert is_healthy

    @mock.patch.object(HealthProbeManagement, "ping_database")
    @mock.patch.object(HealthProbeManagement, "ping_cache")
    @pytest.mark.parametrize(
        "current_app_mode, db_ping_thrown_error, cache_ping_thrown_error",
        (
            # The `PRIVATE_API` needs both the db and cache to be healthy at once
            [
                enums.AppMode.PRIVATE_API.value,
                HealthProbeForDatabaseFailedError,
                HealthProbeForCacheFailedError,
            ],
            [enums.AppMode.PRIVATE_API.value, None, HealthProbeForCacheFailedError],
            [
                enums.AppMode.PRIVATE_API.value,
                HealthProbeForDatabaseFailedError,
                HealthProbeForCacheFailedError,
            ],
            # The `PUBLIC_API` always needs the db, the cache is irrelevant
            [enums.AppMode.PUBLIC_API.value, HealthProbeForDatabaseFailedError, None],
            [
                enums.AppMode.PUBLIC_API.value,
                HealthProbeForDatabaseFailedError,
                HealthProbeForCacheFailedError,
            ],
            # The `CMS_ADMIN` always needs the db, the cache is irrelevant
            [enums.AppMode.CMS_ADMIN.value, HealthProbeForDatabaseFailedError, None],
            [
                enums.AppMode.CMS_ADMIN.value,
                HealthProbeForDatabaseFailedError,
                HealthProbeForCacheFailedError,
            ],
            # The `INGESTION` only needs the db, the cache is irrelevant
            [enums.AppMode.INGESTION.value, HealthProbeForDatabaseFailedError, None],
            [
                enums.AppMode.INGESTION.value,
                HealthProbeForDatabaseFailedError,
                HealthProbeForCacheFailedError,
            ],
            # The `FEEDBACK_API` does not need the db or the cache
            # and as such will not return an unhealthy ping so is omitted
        ),
    )
    def test_returns_false_if_relevant_probes_are_unhealthy_for_selected_app_mode(
        self,
        mocked_ping_cache: mock.MagicMock,
        mocked_ping_database: mock.MagicMock,
        current_app_mode: str,
        db_ping_thrown_error: HealthProbeForDatabaseFailedError | None,
        cache_ping_thrown_error: HealthProbeForCacheFailedError | None,
        monkeypatch,
    ):
        """
        Given a valid `APP_MODE` env var
        And the relevant probes are unhealthy
        When `perform_health_check()` is called
            from an instance of `HealthProbeManagement`
        Then False is returned

        Patches:
            `mocked_ping_cache`: To simulate the
                result of the ping being made to the cache
            `mocked_ping_database`: To simulate the
                result of the ping being made to the db

        """
        # Given
        monkeypatch.setenv(name="APP_MODE", value=current_app_mode)
        mocked_ping_database.side_effect = db_ping_thrown_error
        mocked_ping_cache.side_effect = cache_ping_thrown_error

        health_probe_management = HealthProbeManagement()

        # When
        is_healthy: bool = health_probe_management.perform_health_check()

        # Then
        assert not is_healthy

    # Tests for the cache probe

    @mock.patch.object(HealthProbeManagement, "_get_redis_client")
    def test_ping_cache_returns_true_if_ping_returns_healthy_true(
        self, mocked_get_redis_client: mock.MagicMock
    ):
        """
        Given a cache connection
            which returns True from the `ping()` method
        When `ping_cache()` is called from
            an instance of `HealthProbeManagement`
        Then None is returned and no error is raised
        """
        # Given
        mocked_redis_client = mock.Mock()
        mocked_redis_client.ping.return_value = True
        mocked_get_redis_client.return_value = mocked_redis_client
        health_probe_management = HealthProbeManagement()

        # When
        cache_ping = health_probe_management.ping_cache()

        # Then
        assert cache_ping is None

    @mock.patch.object(HealthProbeManagement, "_get_redis_client")
    def test_ping_cache_raises_error_if_ping_returns_unhealthy_false(
        self, mocked_get_redis_client: mock.MagicMock
    ):
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
        mocked_get_redis_client.return_value = mocked_cache_connection
        health_probe_management = HealthProbeManagement()

        # When / Then
        with pytest.raises(HealthProbeForCacheFailedError):
            health_probe_management.ping_cache()

    @mock.patch.object(HealthProbeManagement, "_get_redis_client")
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
    def test_ping_cache_raises_error_if_ping_throws_error(
        self, mocked_get_redis_client: mock.MagicMock, exception: Exception
    ):
        """
        Given a cache connection
            which raises an error from the `ping()` method
        When `ping_cache()` is called from
            an instance of `HealthProbeManagement`
        Then a `HealthProbeForCacheFailedError` is raised
        """
        # Given
        mocked_redis_client = mock.Mock()
        mocked_redis_client.ping.side_effect = exception
        mocked_get_redis_client.return_value = mocked_redis_client
        health_probe_management = HealthProbeManagement()

        # When / Then
        with pytest.raises(HealthProbeForCacheFailedError):
            health_probe_management.ping_cache()

    # Tests for the database probe

    @mock.patch.object(HealthProbeManagement, "_fetch_row_from_db")
    def test_ping_database_does_not_raise_error_if_healthy(
        self, mocked_fetch_row_from_db: mock.MagicMock
    ):
        """
        Given a database connection
            which returns a valid row
        When `ping_database()` is called from
            an instance of `HealthProbeManagement`
        Then None is returned and no error is raised
        """
        # Given
        mocked_fetch_row_from_db.return_value = (1,)
        health_probe_management = HealthProbeManagement(cache_connection=mock.Mock())

        # When
        db_ping = health_probe_management.ping_database()

        # Then
        assert db_ping is None

    @mock.patch.object(HealthProbeManagement, "_fetch_row_from_db")
    def test_ping_database_raises_error_if_unhealthy(
        self, mocked_fetch_row_from_db: mock.MagicMock
    ):
        """
        Given a database connection
            which returns None when fetching a row
        When `ping_database()` is called from
            an instance of `HealthProbeManagement`
        Then a `HealthProbeForDatabaseFailedError` is raised
        """
        # Given
        mocked_fetch_row_from_db.return_value = None
        health_probe_management = HealthProbeManagement(cache_connection=mock.Mock())

        # When / Then
        with pytest.raises(HealthProbeForDatabaseFailedError):
            health_probe_management.ping_database()

    @mock.patch.object(HealthProbeManagement, "_fetch_row_from_db")
    def test_ping_database_raises_error_if_ping_throws_error(
        self, mocked_fetch_row_from_db: mock.MagicMock
    ):
        """
        Given a database connection
            which throws an error when fetching a row
        When `ping_database()` is called from
            an instance of `HealthProbeManagement`
        Then a `HealthProbeForDatabaseFailedError` is raised
        """
        # Given
        mocked_fetch_row_from_db.side_effect = ConnectionError
        health_probe_management = HealthProbeManagement(cache_connection=mock.Mock())

        # When / Then
        with pytest.raises(HealthProbeForDatabaseFailedError):
            health_probe_management.ping_database()
