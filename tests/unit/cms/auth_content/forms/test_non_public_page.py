from unittest.mock import patch, MagicMock, Mock

from cms.auth_content.forms.non_public_page import (
    NonPublicPageAdminForm,
    SUB_THEME_FIELD,
    TOPIC_FIELD,
)


class TestNonPublicPageAdminForm:

    def test__get_field_choices_returns_correct_structure(self):
        """
        Given a field value and a placeholder
        When _get_field_choices is called
        Then the correct choices are returned
        """
        result = NonPublicPageAdminForm._get_field_choices(42, "Select theme first")
        assert result == [("", "Select theme first"), (42, "Loading... (ID: 42)")]

    def test__initialize_dependent_fields(self):
        """
        Given a mock NonPublicPageAdminForm with initialised fields for sub-theme and topic
        When _initialize_dependent_fields is called
        Then _get_field_choices is called correctly
        """
        # given
        form_mock = MagicMock(
            fields={
                SUB_THEME_FIELD.name: MagicMock(),
                TOPIC_FIELD.name: MagicMock(),
            },
            # give sub-theme a value, but not topic
            instance=MagicMock(**{SUB_THEME_FIELD.name: "4", TOPIC_FIELD.name: None}),
            _get_field_choices=MagicMock(),
        )

        # when
        NonPublicPageAdminForm._initialize_dependent_fields(form_mock)

        # then
        assert (
            form_mock.fields[SUB_THEME_FIELD.name].widget.choices
            == form_mock._get_field_choices.return_value
        )
        form_mock._get_field_choices.assert_called_once_with(
            "4", SUB_THEME_FIELD.choice_default
        )
