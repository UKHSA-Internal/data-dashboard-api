import pytest

from ingestion.utils import enums


@pytest.fixture
def valid_payload_for_base_model() -> dict[str, str]:
    return {
        "parent_theme": "infectious_disease",
        "child_theme": "respiratory",
        "topic": enums.Topic.COVID_19.value,
        "metric_group": enums.DataSourceFileType.testing.value,
        "metric": "COVID-19_testing_PCRcountByDay",
        "geography_type": enums.GeographyType.NATION.value,
        "geography": "England",
        "geography_code": "E92000001",
        "age": "all",
        "sex": "all",
        "stratum": "default",
        "refresh_date": "2024-01-01 14:20:03",
    }
