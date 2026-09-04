import pytest
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from cms.auth_content.models.permission_sets import PermissionSet, PermissionSetForm


class TestPermissionSetForm:
    MOCK_PERMISSION_SET_FIELDS = [
        {"field_name": "theme", "field_label": "Theme"},
        {"field_name": "sub_theme", "field_label": "Sub Theme"},
        {"field_name": "topic", "field_label": "Topic"},
        {"field_name": "metric", "field_label": "Metric"},
        {"field_name": "geography_type", "field_label": "Geography Type"},
        {"field_name": "geography", "field_label": "Geography"},
    ]

    def _make_form(self, instance=None, queryset_exists=False, data=None):
        """
        Instantiate PermissionSetForm with all Wagtail
        internals patched.
        """
        with (
            patch(
                "wagtail.admin.panels.WagtailAdminPageForm.__init__", return_value=None
            ),
            patch(
                "cms.auth_content.models.permission_sets.PERMISSION_SET_FIELDS",
                self.MOCK_PERMISSION_SET_FIELDS,
            ),
            patch(
                "cms.auth_content.models.permission_sets._create_form_field",
                side_effect=lambda field, wildcard: MagicMock(name=field["field_name"]),
            ),
        ):
            form = PermissionSetForm.__new__(PermissionSetForm)
            form.fields = {}
            form.instance = instance or MagicMock(pk=None)
            form.is_bound = data is not None
            form.data = data or {}
            default_data = {
                "theme": 1,
                "sub_theme": 2,
                "topic": 3,
                "metric": 4,
                "geography_type": 5,
                "geography": 6,
            }
            form.cleaned_data = default_data
            form.__init__()

            mock_qs = MagicMock()
            mock_qs.exists.return_value = queryset_exists
            mock_qs.exclude.return_value = mock_qs

            form._mock_qs = mock_qs
            return form

    def test_init_sets_up_fields(self):
        """
        When a new form is instantiated
        Then a form field is added to `fields` for each entry in `PERMISSION_SET_FIELDS`
        """
        form = self._make_form()

        assert len(form.fields) == 6
        assert "theme" in form.fields
        assert "sub_theme" in form.fields
        assert "topic" in form.fields
        assert "metric" in form.fields
        assert "geography_type" in form.fields
        assert "geography" in form.fields

    def test_initialize_dependent_fields_for_saved_instance(self):
        """
        Given a new form
        When an instance has a pk value set
        Then `_initialize_dependent_fields` is called
        """
        instance = MagicMock(pk=1, sub_theme=1, topic=2, metric=3, geography=4)
        form = self._make_form(instance=instance)

        assert form.fields["sub_theme"].widget.choices == [
            ("", "Select theme first"),
            (1, "Loading... (ID: 1)"),
        ]
        assert form.fields["topic"].widget.choices == [
            ("", "Select sub-theme first"),
            (2, "Loading... (ID: 2)"),
        ]
        assert form.fields["metric"].widget.choices == [
            ("", "Select topic first"),
            (3, "Loading... (ID: 3)"),
        ]
        assert form.fields["geography"].widget.choices == [
            ("", "Select geography type first"),
            (4, "Loading... (ID: 4)"),
        ]

    def test_does_not_initialize_dependent_fields_for_unbound_instance(self):
        """
        Given a new unbound form
        When the instance does not have a pk value set
        then `_initialize_dependent_fields` is not called
        """
        with patch.object(
            PermissionSetForm, "_initialize_dependent_fields"
        ) as mock_initialize_dependent_fields:
            self._make_form(instance=MagicMock(pk=None))

        mock_initialize_dependent_fields.assert_not_called()
        
    def test_initialize_dependent_fields_from_bound_data_for_new_instance(self):
        """
        Given a bound form for a new instance
        When the form is re-rendered after validation fails
        The submitted dependent values are added to their dropdown choices
        """
        data = {
            "theme": "1",
            "sub_theme": "2",
            "topic": "3",
            "metric": "4",
            "geography_type": "5",
            "geography": "E92000001",
        }

        form = self._make_form(instance=MagicMock(pk=None), data=data)

        assert form.fields["sub_theme"].widget.choices == [
            ("", "Select theme first"),
            ("2", "Loading... (ID: 2)"),
        ]

        assert form.fields["topic"].widget.choices == [
            ("", "Select sub-theme first"),
            ("3", "Loading... (ID: 3)"),
        ]

        assert form.fields["metric"].widget.choices == [
            ("", "Select topic first"),
            ("4", "Loading... (ID: 4)"),
        ]

        assert form.fields["geography"].widget.choices == [
            ("", "Select geography type first"),
            ("E92000001", "Loading... (ID: E92000001)"),
        ]

    def test_get_field_choices(self):
        """
        When the static function `_get_field_choices` is called without a wildcard
        Then the result returns the placeholder value
        """
        result = PermissionSetForm._get_field_choices("test", "placeholder", None)
        assert result == [("", "placeholder"), ("test", "Loading... (ID: test)")]

    def test_get_field_choices_wildcard_match(self):
        """
        When the static function `_get_field_choices` is called with a wildcard
        Then the result returns the wildcard match
        """
        result = PermissionSetForm._get_field_choices("-1", "placeholder", "wildcard")
        assert result == [("-1", "wildcard")]

    @patch("cms.auth_content.models.permission_sets.PermissionSet.objects.filter")
    def test_validation_error_raised_if_queryset_duplicated(
        self, mock_query_filter: MagicMock
    ):
        """
        Given a form is created with an existing queryset match
        When `clean` is called
        Then a `ValidationError` is raised
        """
        form = self._make_form(queryset_exists=True)
        mock_query_filter.return_value = form._mock_qs

        with pytest.raises(ValidationError) as e:
            form.clean()

        assert (
            "A permission set with this exact combination already exists. Please modify your selection to create a unique permission set."
            in str(e.value)
        )

    @patch("cms.auth_content.models.permission_sets.PermissionSet.objects.filter")
    def test_returns_cleaned_data_when_no_duplicate_exists(
        self, mock_query_filter: MagicMock
    ):
        """
        Given a form is created without an existing queryset match
        When `clean` is called
        Then the cleaned data is returned
        """
        instance = MagicMock(pk=1)
        form = self._make_form(instance=instance, queryset_exists=False)
        mock_query_filter.return_value = form._mock_qs

        result = form.clean()

        assert result == form.cleaned_data


class TestPermissionSet:
    def test_get_choice_label(self):
        """
        Given a blank `PermissionSet`
        When `_get_choice_label` is called with an unknown field and value
        Then the unknown value is returned
        """
        test_permission_set = PermissionSet()
        unknown_field = "unknown_field_type"
        test_value = "12345"

        # When
        result = test_permission_set._get_choice_label(unknown_field, test_value)

        # Then
        assert result == test_value
