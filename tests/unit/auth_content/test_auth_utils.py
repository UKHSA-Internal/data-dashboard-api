import pytest
from unittest.mock import MagicMock
from django import forms

from cms.auth_content.auth_utils import _create_form_field


class TestCreateFormField:
    def test_create_form_field_basic(self):
        """
        Given no wildcard or callables in data
        When `_create_form_field` is called
        Then only the default choices are returned
        """
        field_data = {
            "field_choice_default": "Select an option",
            "field_choice_wildcard": None,
            "field_choice_callable": None,
            "field_label": "My Label",
        }

        result = _create_form_field(field_data)

        assert isinstance(result, forms.CharField)
        assert result.label == "My Label"
        expected_choices = [("", "Select an option")]
        assert result.widget.choices == expected_choices

    def test_create_form_field_with_wildcard(self):
        """
        Given a wildcard in the data
        When `_create_form_field` is called
        Then the wildcard choice is added
        """
        field_data = {
            "field_choice_default": "Default",
            "field_choice_wildcard": "All Items",
            "field_choice_callable": None,
            "field_label": "Label",
        }
        wildcard_val = "-1"

        result = _create_form_field(field_data, wildcard_id_value=wildcard_val)

        expected_choices = [("", "Default"), ("-1", "All Items")]
        assert result.widget.choices == expected_choices

    def test_create_form_field_with_callable(self):
        """
        Given a callable in the data
        When `_create_form_field` is called
        Then the callable choice is added
        """
        mock_callable = MagicMock(return_value=[("1", "One"), ("2", "Two")])

        field_data = {
            "field_choice_default": "Default",
            "field_choice_wildcard": None,
            "field_choice_callable": mock_callable,
            "field_label": "Label",
        }

        result = _create_form_field(field_data)

        expected_choices = [("", "Default"), ("1", "One"), ("2", "Two")]
        assert result.widget.choices == expected_choices
        mock_callable.assert_called_once()

    def test_create_form_field_all_features(self):
        """
        Given both a wildcard and callable are in the data
        When `_create_form_field` is called
        Then both the wildcard and callable choices are added
        """
        """Test combined default, wildcard, and callable choices"""
        mock_callable = MagicMock(return_value=[("dynamic", "Dynamic")])
        field_data = {
            "field_choice_default": "Default",
            "field_choice_wildcard": "Wildcard",
            "field_choice_callable": mock_callable,
            "field_label": "Label",
        }

        result = _create_form_field(field_data, wildcard_id_value="999")

        expected_choices = [
            ("", "Default"),
            ("999", "Wildcard"),
            ("dynamic", "Dynamic"),
        ]
        assert result.widget.choices == expected_choices

    def test_create_form_field_missing_key_error(self):
        """
        Given data with missing keys
        When `_create_form_field` is called
        Then a key error exception is raised
        """
        """Test behavior if a required key is missing from the dict"""
        field_data = {"field_choice_default": "Missing other keys"}

        with pytest.raises(KeyError):
            _create_form_field(field_data)
