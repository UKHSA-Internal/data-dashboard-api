from dataclasses import dataclass
from unittest.mock import patch, MagicMock

import pytest

from tests.migrations.helper import MigrationTests


@dataclass
class Scenario:
    is_public: bool
    page_classification: str | None
    theme: str | None
    sub_theme: str | None
    topic: str | None
    metric: str


@pytest.mark.django_db(transaction=True)
class Test0018_metricsdocumentationchildentry_page_sub_theme_and_more(MigrationTests):
    previous_migration_name = "0017_alter_metricsdocumentationchildentry_topic"
    current_migration_name = (
        "0018_metricsdocumentationchildentry_page_sub_theme_and_more"
    )
    current_django_app = "metrics_documentation"

    def create_mdce(self, number: int = 1, **kwargs):
        ContentType = self.get_model("ContentType", app="contenttypes")
        Locale = self.get_model("Locale", app="wagtailcore")
        MetricsDocumentationChildEntry = self.get_model(
            "MetricsDocumentationChildEntry"
        )

        locale, _ = Locale.objects.get_or_create(language_code="en")
        mdce_content_type, _ = ContentType.objects.get_or_create(
            app_label="metrics_documentation",
            model="metricsdocumentationchildentry",
        )

        return MetricsDocumentationChildEntry.objects.create(
            title=f"MDCE {number}",
            draft_title=f"MDCE {number}",
            slug=f"mdce-{number}",
            path=f"9001000{number}",
            depth=2,
            numchild=0,
            url_path=f"/mdce-{number}/",
            content_type_id=mdce_content_type.id,
            locale_id=locale.id,
            page_description=f"An mdce page numbered {number}",
            seo_title=f"mdce-{number}",
            **kwargs,
        )

    def get_mdce_page(self, number: int = 1):
        return self.get_model("MetricsDocumentationChildEntry").objects.get(
            title=f"MDCE {number}"
        )

    @pytest.mark.parametrize(
        "start, after_forward, after_backward",
        [
            # a public MDCE with a string metric and topic
            (
                Scenario(
                    is_public=True,
                    page_classification=None,
                    theme="",
                    sub_theme="",
                    topic="COVID-19",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
                Scenario(
                    is_public=True,
                    page_classification="",
                    theme="",
                    sub_theme="",
                    topic="",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
                Scenario(
                    is_public=True,
                    page_classification="",
                    theme="",
                    sub_theme="",
                    topic="COVID-19",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
            ),
            # a public MDCE with a missing topic and an ID metric
            (
                Scenario(
                    is_public=True,
                    page_classification=None,
                    theme=None,
                    sub_theme=None,
                    topic=None,
                    metric="123",
                ),
                Scenario(
                    is_public=True,
                    page_classification="",
                    theme="",
                    sub_theme="",
                    topic="",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
                Scenario(
                    is_public=True,
                    page_classification="",
                    theme=None,
                    sub_theme=None,
                    topic=None,
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
            ),
            # a public MDCE page with IDs for both metric and topic
            (
                Scenario(
                    is_public=True,
                    page_classification=None,
                    theme=None,
                    sub_theme=None,
                    topic="200",
                    metric="123",
                ),
                Scenario(
                    is_public=True,
                    page_classification="",
                    theme="",
                    sub_theme="",
                    topic="",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
                Scenario(
                    is_public=True,
                    page_classification="",
                    theme=None,
                    sub_theme=None,
                    topic="200",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
            ),
            # a non-public MDCE with IDs for metric and topic
            (
                Scenario(
                    is_public=False,
                    page_classification="official-sensitive",
                    theme="1",
                    sub_theme="2",
                    topic="3",
                    metric="123",
                ),
                Scenario(
                    is_public=False,
                    page_classification="official-sensitive",
                    theme="1",
                    sub_theme="2",
                    topic="3",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
                Scenario(
                    is_public=False,
                    page_classification="official-sensitive",
                    theme="1",
                    sub_theme="2",
                    topic="3",
                    metric="COVID-19_headline_cases_7DayTotals",
                ),
            ),
        ],
    )
    def test_scenarios(
        self,
        monkeypatch,
        start: Scenario,
        after_forward: Scenario,
        after_backward: Scenario,
    ):
        # Given
        self.migrate_backward()

        self.create_mdce(
            is_public=start.is_public,
            metric=start.metric,
            topic=start.topic,
            page_classification=start.page_classification,
            theme=start.theme,
            sub_theme=start.sub_theme,
        )

        get_metric_id_to_name_mapping_mock = MagicMock(
            return_value={"123": "COVID-19_headline_cases_7DayTotals"}
        )
        get_metric_name_to_topic_id_mapping_mock = MagicMock(
            return_value={"COVID-19_headline_cases_7DayTotals": "COVID-19"}
        )
        monkeypatch.setattr(
            "cms.metrics_documentation.migrations."
            "0018_metricsdocumentationchildentry_page_sub_theme_and_more."
            "get_metric_id_to_name_mapping",
            get_metric_id_to_name_mapping_mock,
        )
        monkeypatch.setattr(
            "cms.metrics_documentation.migrations."
            "0018_metricsdocumentationchildentry_page_sub_theme_and_more."
            "get_metric_name_to_topic_id_mapping",
            get_metric_name_to_topic_id_mapping_mock,
        )

        mdce_page = self.get_mdce_page()
        assert mdce_page.is_public == start.is_public
        assert mdce_page.page_classification == start.page_classification
        assert mdce_page.metric == start.metric
        assert mdce_page.theme == start.theme
        assert mdce_page.sub_theme == start.sub_theme
        assert mdce_page.topic == start.topic

        # When
        self.migrate_forward()
        # Then
        mdce_page = self.get_mdce_page()
        assert mdce_page.is_public == after_forward.is_public
        assert mdce_page.page_classification == after_forward.page_classification
        assert mdce_page.metric == after_forward.metric
        assert mdce_page.page_theme == after_forward.theme
        assert mdce_page.page_sub_theme == after_forward.sub_theme
        assert mdce_page.page_topic == after_forward.topic

        # When
        self.migrate_backward()
        # Then
        mdce_page = self.get_mdce_page()
        assert mdce_page.is_public == after_backward.is_public
        assert mdce_page.page_classification == after_backward.page_classification
        assert mdce_page.metric == after_backward.metric
        assert mdce_page.theme == after_backward.theme
        assert mdce_page.sub_theme == after_backward.sub_theme
        assert mdce_page.topic == after_backward.topic
