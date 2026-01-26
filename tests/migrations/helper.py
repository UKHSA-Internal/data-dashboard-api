import sys

from django.apps import apps
from django.db import connection, models
from django.db.migrations.executor import MigrationExecutor
import pytest

REASON = "Migration tests are excluded from coverage test runs"


@pytest.mark.skipif(condition="--cov" in sys.argv, reason=REASON)
class MigrationTests:
    """Used to test django migrations.

    Notes:
        When testing migrations, ensure your test class inherits from this.
        Define the following attributes:
         - `previous_migration_name` e.g. 0001_initial
         - `current_migration_name`  e.g. 0002_new_field_added_to_model_a
         - `current_django_app`      e.g. metrics_documentation

        Call `self.migrate_back()` to roll the project state to the previous node.
        Call `self.migrate_forward()` to roll the project state to the current node.
        At any given point, call `get_model()` with the name of the model
            you are interested in to get that model state at that point in time.

        Tests which inherit from this test helper class
        will also be excluded from the test suite
        when the --cov arg is used. i.e. for test coverage runs

    """

    application_registry = apps

    @property
    def previous_migration_name(self) -> str:
        raise NotImplementedError(
            "Provide the `previous_migration_name` to the test class"
        )

    @property
    def current_migration_name(self) -> str:
        raise NotImplementedError(
            "Provide the `current_migration_name` to the test class"
        )

    @property
    def current_django_app(self) -> str:
        raise NotImplementedError("Provide the `current_django_app` to the test class")

    @property
    def previous_node(self) -> list[tuple[str, str]]:
        return [(self.current_django_app, self.previous_migration_name)]

    @property
    def current_node(self) -> list[tuple[str, str]]:
        return [(self.current_django_app, self.current_migration_name)]

    @property
    def _migration_executor(self) -> MigrationExecutor:
        return MigrationExecutor(connection=connection)

    def migrate_to_node(self, node: list[tuple[str, str]]) -> None:
        """Migrates the state of the project to the given `node`

        Args:
            `node`: The node to be migrated to.
                To be provided with the current app and migration name

        """
        # Migrate to the given node
        migration_executor = self._migration_executor
        migration_executor.migrate(targets=node)

        # Load the project state of the application at the point of the new migration node
        self.application_registry = migration_executor.loader.project_state(
            nodes=node
        ).apps

    def migrate_backward(self) -> None:
        """Migrates the project state to the node associated with the `previous_migration_name`"""
        self.migrate_to_node(node=self.previous_node)

    def migrate_forward(self) -> None:
        """Migrates the project state to the node associated with the `current_migration_name`"""
        self.migrate_to_node(node=self.current_node)

    def get_model(self, name: str) -> models.base.ModelBase:
        """Returns the model associated with the `name` at the current project state

        Args:
            name: The name of the model
                E.g. "MetricsDocumentationChildEntry"

        Returns:
            A class representing a snapshot of the model at the current project state

        """
        return self.application_registry.get_model(
            app_label=self.current_django_app, model_name=name
        )
