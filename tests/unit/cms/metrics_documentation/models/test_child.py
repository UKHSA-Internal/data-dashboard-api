from unittest import mock
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
import pytest
from wagtail.admin.panels import FieldPanel
from wagtail.api.conf import APIField

from cms.dashboard.constants import THEME_FIELDS
from cms.metrics_documentation.models.child import (
    MetricsDocumentationChildEntryAdminForm,
    InvalidTopicForChosenMetricForChildEntryError,
)
from tests.fakes.factories.cms.metrics_documentation_child_entry_factory import (
    FakeMetricsDocumentationChildEntryFactory,
)

MODULE_PATH = "cms.metrics_documentation.models.child"


class TestInvalidTopicForChosenMetricForChildEntryError:
    def test_exception_has_expected_message(self):
        actual = InvalidTopicForChosenMetricForChildEntryError(
            "test_topic", "test_metric"
        )
        expected = "InvalidTopicForChosenMetricForChildEntryError('The `test_topic` is not available for selected metric of `test_metric`')"

        assert expected == repr(actual)


class TestMetricsDocumentationChildEntryAdminForm:
    MOCK_THEME_FIELDS = [
        {"field_name": "theme", "label": "Theme", "required": True},
        {"field_name": "sub_theme", "label": "Sub Theme", "required": False},
        {"field_name": "topic", "label": "Topic", "required": False},
    ]

    def _make_form(self, instance=None):
        """
        Instantiate MetricsDocumentationChildEntryAdminForm with all Wagtail
        internals patched.
        """
        with (
            patch(
                "wagtail.admin.panels.WagtailAdminPageForm.__init__", return_value=None
            ),
            patch(
                "cms.metrics_documentation.models.child.THEME_FIELDS",
                self.MOCK_THEME_FIELDS,
            ),
            patch(
                "cms.metrics_documentation.models.child._create_form_field",
                side_effect=lambda field: MagicMock(name=field["field_name"]),
            ),
        ):
            form = MetricsDocumentationChildEntryAdminForm.__new__(
                MetricsDocumentationChildEntryAdminForm
            )
            form.fields = {}
            form.instance = instance or MagicMock(pk=None)
            form.__init__()
            return form

    def _make_form_with_instance(self, sub_theme=None, topic=None):
        """
        Instantiate MetricsDocumentationChildEntryAdminForm with all Wagtail
        internals patched, and a mocked instance.
        """
        instance = MagicMock(pk=1)
        instance.sub_theme = sub_theme
        instance.topic = topic

        form = self._make_form(instance=instance)

        for field_name in ("sub_theme", "topic"):
            mock_widget = MagicMock()
            mock_widget.choices = []
            form.fields[field_name] = MagicMock(widget=mock_widget)

        return form

    def test_creates_field_for_every_theme_field(self):
        """
        When a new form is instantiated
        Then a form field is added to `fields` for each entry in `THEME_FIELDS`.
        """
        form = self._make_form()

        assert len(form.fields) == 3
        assert "theme" in form.fields
        assert "sub_theme" in form.fields
        assert "topic" in form.fields

    @mock.patch("cms.metrics_documentation.models.child._create_form_field")
    @mock.patch("wagtail.admin.panels.WagtailAdminPageForm.__init__")
    def test_field_creation_uses_create_form_field_helper(
        self, spy_init_admin_form: mock.MagicMock, spy_create_form_field: mock.MagicMock
    ):
        """
        Given a new form is created
        When init is called on the form
        Then `_create_form_field` is called once per `THEME_FIELDS` entry.
        """
        form = MetricsDocumentationChildEntryAdminForm.__new__(
            MetricsDocumentationChildEntryAdminForm
        )
        form.fields = {}
        form.instance = MagicMock(pk=None)
        form.__init__()

        assert spy_create_form_field.call_count == len(THEME_FIELDS)
        spy_create_form_field.assert_any_call(THEME_FIELDS[0])
        spy_create_form_field.assert_any_call(THEME_FIELDS[1])
        spy_create_form_field.assert_any_call(THEME_FIELDS[2])
        spy_create_form_field.assert_any_call(THEME_FIELDS[3])

    def test_initialize_dependent_fields_called_when_instance_has_pk(self):
        """
        Given a new form
        When an instance has a pk value set
        Then `_initialize_dependent_fields` is called
        """
        instance = MagicMock(pk=42)

        with patch.object(
            MetricsDocumentationChildEntryAdminForm,
            "_initialize_dependent_fields",
        ) as mock_init_deps:
            self._make_form(instance=instance)

        mock_init_deps.assert_called_once()

    def test_initialize_dependent_fields_called_when_instance_has_no_pk(self):
        """
        Given a new form
        When an instance does not have a pk value set
        Then `_initialize_dependent_fields` is not called
        """
        instance = MagicMock(pk=None)

        with patch.object(
            MetricsDocumentationChildEntryAdminForm,
            "_initialize_dependent_fields",
        ) as mock_init_deps:
            self._make_form(instance=instance)

        mock_init_deps.assert_not_called()

    def test_both_fields_updated_when_both_have_values(self):
        """
        Given a new form with a sub_theme and topic
        When `_initialize_dependent_fields` is called
        Then both sub_theme and topic choices are set
        """
        form = self._make_form_with_instance(sub_theme=3, topic=7)

        form._initialize_dependent_fields()

        assert form.fields["sub_theme"].widget.choices == [
            ("", "Select theme first"),
            (3, "Loading... (ID: 3)"),
        ]
        assert form.fields["topic"].widget.choices == [
            ("", "Select sub-theme first"),
            (7, "Loading... (ID: 7)"),
        ]

    def test_skips_field_when_value_is_none(self):
        """
        Given a new form with no sub_theme or topic
        When `_initialize_dependent_fields` is called
        Then widget choices are left untouched.
        """
        form = self._make_form_with_instance(sub_theme=None, topic=None)
        original_choices = form.fields["sub_theme"].widget.choices

        form._initialize_dependent_fields()

        assert form.fields["sub_theme"].widget.choices == original_choices


class TestMetricsDocumentationChildEntry:
    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "title",
            "body",
            "metric",
            "metric_group",
            "topic",
            "last_updated_at",
            "last_published_at",
            "page_description",
            "is_public",
            "page_classification",
        ],
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_has_correct_api_fields(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        expected_api_field: str,
    ):
        """
        Given blank `MetricsDocumentationChildEntryPage` model.
        When `api_fields` is called.
        Then the expected names are on the returned `APIField` objects.
        """
        # Given
        fake_metrics_documentation_child_entry = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        api_fields: list[APIField] = fake_metrics_documentation_child_entry.api_fields

        # Then
        api_fields_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field in api_fields_names

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "page_description",
            "metric",
            "body",
        ],
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_has_the_correct_content_panels(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        expected_content_panel_name: str,
    ):
        """
        Give a blank `MetricsDocumentationChildEntryPage` model.
        When the expected content panel name is called
        Then the panel value can be accessed from the page model
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        content_panels: list[FieldPanel] = (
            fake_metrics_documentation_child_entry_page.content_panels
        )

        # Then
        assert hasattr(
            fake_metrics_documentation_child_entry_page, expected_content_panel_name
        )

    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    @pytest.mark.parametrize(
        "metric_id, metric_group",
        [
            (1, "cases"),
            (2, "headline"),
            (3, "vaccinations"),
            (4, "deaths"),
        ],
    )
    def test_metric_group_returns_expected_string(
        self,
        get_all_metric_names_and_ids: mock.MagicMock,
        metric_id: int,
        metric_group: str,
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric id is supplied to the `metric` property.
        Then the metric_group will be correctly extracted from the string.
        """
        # Given
        get_all_metric_names_and_ids.return_value = [
            (1, "COVID-19_cases_rateRollingMean"),
            (2, "COVID-19_headline_vaccines_autumn23Total"),
            (3, "COVID-19_vaccinations_autumn22_uptakeByDay"),
            (4, "COVID-19_deaths_ONSByWeek"),
        ]
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = metric_id

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == metric_group

    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    @pytest.mark.parametrize(
        "metric_id",
        [1, 2, 3, 4, 5],
    )
    def test_metric_group_returns_emptry_string_with_missing_values(
        self, get_all_metric_names_and_ids: mock.MagicMock, metric_id: int
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric id is supplied to the `metric` property with invalid choices returned.
        Then the metric_group will return an empty string.
        """
        # Given
        get_all_metric_names_and_ids.return_value = [
            (1, "COVID-19casesrateRollingMean"),
            (2, "COVID-19_"),
            (3, ""),
            (4, None),
        ]
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = metric_id

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == ""

    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_metric_group_returns_emptry_string_with_empty_metrics(
        self, get_all_metric_names_and_ids: mock.MagicMock
    ):
        """
        Given a blank `MetricsDocumentationChildEntryPage` model.
        When a metric id is supplied to the `metric` property with no choices returned.
        Then the metric_group will return an empty string.
        """
        # Given
        get_all_metric_names_and_ids.return_value = []
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        # When
        fake_metrics_documentation_child_entry_page.metric = 1

        # Then
        assert fake_metrics_documentation_child_entry_page.metric_group == ""

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_error_raised_if_invalid_classification(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When no page classification is given.
        Then a `ValidationError` is raised.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = None
        fake_metrics_documentation_child_entry_page.theme = "test"
        fake_metrics_documentation_child_entry_page.sub_theme = "test"
        fake_metrics_documentation_child_entry_page.topic = "test"

        # When/Then
        with pytest.raises(ValidationError) as e:
            fake_metrics_documentation_child_entry_page.clean()

        assert "Please select a classification level for this non-public page" in str(
            e.value
        )

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_error_raised_if_invalid_theme(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When no theme is given.
        Then a `ValidationError` is raised.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = "test"
        fake_metrics_documentation_child_entry_page.theme = None
        fake_metrics_documentation_child_entry_page.sub_theme = "test"
        fake_metrics_documentation_child_entry_page.topic = "test"

        # When/Then
        with pytest.raises(ValidationError) as e:
            fake_metrics_documentation_child_entry_page.clean()

        assert "Please select a theme for this non-public page" in str(e.value)

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_error_raised_if_invalid_sub_theme(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When no sub theme is given.
        Then a `ValidationError` is raised.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = "test"
        fake_metrics_documentation_child_entry_page.theme = "None"
        fake_metrics_documentation_child_entry_page.sub_theme = None
        fake_metrics_documentation_child_entry_page.topic = "test"

        # When/Then
        with pytest.raises(ValidationError) as e:
            fake_metrics_documentation_child_entry_page.clean()

        assert "Please select a subtheme for this non-public page" in str(e.value)

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_error_raised_if_invalid_topic(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When no topic is given.
        Then a `ValidationError` is raised.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = "test"
        fake_metrics_documentation_child_entry_page.theme = "test"
        fake_metrics_documentation_child_entry_page.sub_theme = "test"
        fake_metrics_documentation_child_entry_page.topic = None

        # When/Then
        with pytest.raises(ValidationError) as e:
            fake_metrics_documentation_child_entry_page.clean()

        assert "Please select a topic for this non-public page" in str(e.value)

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_public_page_clears_page_classification(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is True (i.e the page is a public page).
        When a page classification is given.
        Then the page classification level is cleared.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = True
        fake_metrics_documentation_child_entry_page.page_classification = "official"

        # When
        fake_metrics_documentation_child_entry_page.clean()

        # Then
        assert fake_metrics_documentation_child_entry_page.page_classification is None

    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_seo_title_tag_not_provided",
        return_value=None,
    )
    @mock.patch(
        "cms.dashboard.models.UKHSAPage._raise_error_if_slug_not_unique",
        return_value=None,
    )
    @mock.patch(f"{MODULE_PATH}.get_all_metric_names_and_ids")
    def test_non_public_page_doesnt_clean_page_classification(
        self,
        mock_get_all_metric_names_and_ids: mock.MagicMock(),
        mock_slug_raise_error,
        mock_seo_title_raise_error,
    ):
        """
        Given is_public is False (i.e the page is a non public page).
        When a page classification is given.
        Then the page classification level is kept.
        """
        # Given
        fake_metrics_documentation_child_entry_page = (
            FakeMetricsDocumentationChildEntryFactory.build_page_from_template()
        )

        fake_metrics_documentation_child_entry_page.is_public = False
        fake_metrics_documentation_child_entry_page.page_classification = "official"
        fake_metrics_documentation_child_entry_page.theme = "infectious_disease"
        fake_metrics_documentation_child_entry_page.sub_theme = "respiratory"
        fake_metrics_documentation_child_entry_page.topic = "COVID-19"

        # When
        fake_metrics_documentation_child_entry_page.clean()

        # Then
        assert (
            fake_metrics_documentation_child_entry_page.page_classification
            == "official"
        )
