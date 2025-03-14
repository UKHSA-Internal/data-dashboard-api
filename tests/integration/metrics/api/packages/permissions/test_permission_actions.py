import pytest

from unittest.mock import MagicMock

from metrics.api.packages.permissions import (
    new_match_dict,
    MatchThemeSubThemeFieldsAction,
    MatchFieldAction,
)

core_headline_data = {
    "theme": "infectious_disease",
    "sub_theme": "respiratory",
    "topic": "COVID-19",
    "geography_type": "",
    "geography": "",
    "metric": "COVID-19_headline_vaccines_spring24Uptake",
    "stratum": "default",
    "sex": "",
    "age": "01-04",
    "metric_value": 123.45,
    "period_start": "2024-01-01 00:00:00",
    "period_end": "2024-02-02 00:00:00",
    "is_private": False,
}


class TestNewMatchDict:

    def test_new_match_dict_returns_expected_dict(self):
        """
        Given no input parameters
        When `new_match_dict()` is called
        Then it returns a dictionary with predefined keys
        And all values are `False`
        """
        # When
        result = new_match_dict()

        # Then
        expected_keys = {
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "age",
            "stratum",
        }

        assert (
            set(result.keys()) == expected_keys
        ), "Unexpected keys in the returned dictionary"

        # And all values should be False
        assert all(
            value is False for value in result.values()
        ), "All values should be False"


class TestMatchTopLevelFieldsAction:

    @pytest.mark.parametrize(
        "field_name,field_value,expected",
        [
            ("theme", "infectious_disease", True),
            ("theme", "WRONG_VALUE", False),
            ("sub_theme", "respiratory", True),
            ("sub_theme", "WRONG_VALUE", False),
        ],
    )
    @pytest.mark.django_db
    def test_execute(self, field_name, field_value, expected):
        """
        Given a `field_name` and `field_value`
        When `execute()` is called with a mock permission object
        Then it returns `True` if the field value matches
        And it returns `False` otherwise
        """
        # Given
        fake_permission = MagicMock()
        fake_permission_field = MagicMock()
        fake_permission_field.name = field_value

        setattr(fake_permission, field_name, fake_permission_field)
        data = core_headline_data

        matched_fields = new_match_dict()
        action = MatchThemeSubThemeFieldsAction(data=data)

        # When
        matched_fields = action.execute(
            field_name=field_name,
            group_permission=fake_permission,
            match_fields=matched_fields,
        )

        # Then
        assert matched_fields[field_name] is expected


class TestMatchFieldAction:

    @pytest.mark.parametrize(
        "field_name,field_value,expected",
        [
            ("theme", "infectious_disease", True),
            ("theme", "WRONG_VALUE", False),
            ("sub_theme", "respiratory", True),
            ("sub_theme", "WRONG_VALUE", False),
            ("topic", "COVID-19", True),
            ("topic", "WRONG_VALUE", False),
        ],
    )
    @pytest.mark.django_db
    def test_execute(self, field_name, field_value, expected):
        """
        Given a `field_name` and `field_value`
        When `execute()` is called with a mock permission object
        Then it returns `True` if the field value matches
        And it returns `False` otherwise
        """
        # Given
        fake_permission = MagicMock()

        # Mock field attribute
        mock_permission_field = MagicMock()
        mock_permission_field.name = field_value
        setattr(fake_permission, field_name, mock_permission_field)

        data = core_headline_data
        action = MatchFieldAction(data=data)
        matched_fields = new_match_dict()
        # When
        matched_fields = action.execute(
            field_name=field_name,
            group_permission=fake_permission,
            match_fields=matched_fields,
        )

        # Then
        assert matched_fields[field_name] is expected
