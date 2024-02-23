import os

import redis
from django.core.cache import cache as django_cache_proxy
from django.db import connection as django_db_proxy
from django.utils.connection import ConnectionProxy

from metrics.api import enums

OPTIONAL_CONNECTION_PROXY = ConnectionProxy | None


class HealthProbeForCacheFailedError(ConnectionError): ...


class HealthProbeForDatabaseFailedError(ConnectionError): ...


class HealthProbeManagement:
    def __init__(
        self,
        cache_connection: OPTIONAL_CONNECTION_PROXY = None,
        database_connection: OPTIONAL_CONNECTION_PROXY = None,
    ):
        self._cache_connection = cache_connection or self._get_redis_client(
            django_cache_proxy=django_cache_proxy
        )
        self._database_connection = database_connection or django_db_proxy

    def perform_health_check(self) -> bool:
        """Probes any dependant infrastructure as dictated by the `APP_MODE` env variable

        Notes:
            For example, the `PRIVATE_API` app mode
            depends on both the database and the cache.
            Whereas, the `FEEDBACK_API` app mode requires neither:

            |   App mode   | Needs db | Needs cache |
            |---------------------------------------|
            | PRIVATE_API  |   Yes    |    Yes      |
            | PUBLIC_API   |   Yes    |     No      |
            | CMS_ADMIN    |   Yes    |     No      |
            | INGESTION    |   Yes    |     No      |
            | FEEDBACK_API |    No    |     No      |

        Returns:
            True if all the dependencies are healthy.
            False otherwise.

        """
        current_app_mode: str = os.environ.get("APP_MODE")

        if current_app_mode in enums.AppMode.dependent_on_db():
            try:
                self.ping_database()
            except HealthProbeForDatabaseFailedError:
                return False

        if current_app_mode in enums.AppMode.dependent_on_cache():
            try:
                self.ping_cache()
            except HealthProbeForCacheFailedError:
                return False

        return True

    # Cache probe

    def ping_cache(self) -> None:
        """Pings the cache to determine if it is reachable

        Returns:
            None

        Raises:
            `HealthProbeForCacheFailedError`: If the
            ping to the cache fails for any reason

        """
        try:
            cache_is_pingable: bool = self._cache_connection.ping()
        except redis.exceptions.RedisError as error:
            raise HealthProbeForCacheFailedError from error

        if not cache_is_pingable:
            raise HealthProbeForCacheFailedError

    @classmethod
    def _get_redis_client(cls, django_cache_proxy: ConnectionProxy) -> redis.Redis:
        """Retrieves the native Redis client from the django cache proxy

        Notes:
            Instead of instantiating a `RedisClient` object seperately,
            this method peels off a new native `RedisClient` from
            the django cache proxy.
            This means we can just take the connection arguments
            as per the django application.

            We need the native `redis.Redis` client object
            instead of the Django Redis wrapper, because
            the latter does not directly expose a `ping()` method.

        Args:
            `django_cache_proxy`: The django cache connection proxy
                which is provided via the Django application
                through `django.core.cache import cache`

        Returns:
            The native `Redis` client object
            which is already connected to the `Redis` cache

        """
        return django_cache_proxy._cache.get_client(  # noqa: SLF001
            key=None, write=False
        )

    # Database probe

    def ping_database(self) -> None:
        """Pings the database to determine if it is reachable

        Returns:
            None

        Raises:
            `HealthProbeForDatabaseFailedError`: If the ping
            to the database fails for any reason

        """
        db_is_usable: bool = self._database_connection.is_usable()
        if not db_is_usable:
            raise HealthProbeForDatabaseFailedError
