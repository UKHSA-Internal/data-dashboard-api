import pytest

from tests.fakes.factories.cms.metrics_documentation_factory import (
    FakeMetricsDocumentationParentPageFactory,
)


@pytest.mark.django_db
def test_metric_documentation_child_entry_forward_migration(migrator):
    app_name = "metrics_documentation"
    previous_node = "0002_metricsdocumentationchildentry"
    old_state = migrator.apply_initial_migration((app_name, previous_node))

    metric_documentation_child_entry_model = old_state.apps.get_model(
        "metrics_documentation", "MetricsDocumentationChildEntry"
    )

    assert not metric_documentation_child_entry_model.objects.count()
