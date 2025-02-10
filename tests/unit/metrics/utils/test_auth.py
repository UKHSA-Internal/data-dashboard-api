import pytest
import os
import copy
from typing import List, Dict

from unittest.mock import MagicMock, patch

from metrics.utils.auth_action import (
    MatchTopLevelFieldsAction,
    MatchFieldAction,
    ValidationAction,
    MatchThemeSubthemeAction,
)
from metrics.utils.auth import (
    authorised_route,
    serializer_permissions,
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

class TestMatchTopLevelFieldsAction:
    @pytest.mark.parametrize(
        "field_name,field_value,expected",
        [
            ("theme", "infectious_disease", True),
            ("theme", "WRONG_VALUE", False),
            ("sub_theme", "respiratory", True),
            ("sub_theme", "WRONG_VALUE", False),
        ]
    )
    @pytest.mark.django_db
    def test_execute(self, field_name, field_value, expected):
        mock_permission = MagicMock()

        mock_permission_theme_field = MagicMock()
        mock_permission_theme_field.name = field_value
        setattr(mock_permission, field_name, mock_permission_theme_field)

        data = core_headline_data
        action = MatchTopLevelFieldsAction(field_name)
        result = action.execute(data, mock_permission)
        assert result is expected, f"{field_name} expected to be {not expected}"


class TestMatchThemeSubthemeAction:

    @pytest.mark.parametrize(
        "theme_name,subtheme_name,expected",
        [
            ("infectious_disease", "respiratory", True),
            ("infectious_disease", "WRONG_VALUE", False),
            ("WRONG_VALUE", "respiratory", False),
        ]
    )
    @pytest.mark.django_db
    def test_execute(self, theme_name, subtheme_name, expected):
        mock_permission = MagicMock()

        mock_permission_theme_field = MagicMock()
        mock_permission_theme_field.name = theme_name

        setattr(mock_permission, "theme", mock_permission_theme_field)

        mock_permission_subtheme_field = MagicMock()
        mock_permission_subtheme_field.name = subtheme_name
        setattr(mock_permission, "sub_theme", mock_permission_subtheme_field)

        data = core_headline_data
        action = MatchThemeSubthemeAction()
        result = action.execute(data, mock_permission)
        assert result is expected, f"theme & sub_theme match expected to be {expected}"


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
        ]
    )
    @pytest.mark.django_db
    def test_execute(self, field_name, field_value, expected):
        mock_permission = MagicMock()

        mock_permission_theme_field = MagicMock()
        mock_permission_theme_field.name = field_value
        setattr(mock_permission, field_name, mock_permission_theme_field)

        data = core_headline_data
        action = MatchFieldAction(field_name)
        result = action.execute(data, mock_permission)
        assert result is expected, f"{field_name} expected to be {not expected}"


class TestValidationAction:

    @pytest.mark.parametrize(
        "matched_plots,did_match",
        [
            ([{"theme": False, "sub_theme": False, "topic": False, "geography_type": False, "geography": False}], False),
            ([{"theme": True, "sub_theme": True, "topic": True, "geography_type": False, "geography": True}], False),
            ([{"theme": True, "sub_theme": True, "topic": True, "geography_type": True, "geography": True}], True),
            ([
                 {"theme": False, "sub_theme": True, "topic": True, "geography_type": True, "geography": True},
                 {"theme": False, "sub_theme": False, "topic": False, "geography_type": False, "geography": False}
             ], False),
            ([
                 {"theme": True, "sub_theme": True, "topic": True, "geography_type": True, "geography": True},
                 {"theme": False, "sub_theme": False, "topic": False, "geography_type": False, "geography": False}
             ], True),
        ]
    )
    def test_execute(self, matched_plots: List[Dict], did_match: bool):
        validated_action = ValidationAction()
        validated_action.execute(matched_plots)
        assert validated_action.did_match is did_match


class MockSerializer:
    def __init__(self, *args, **kwargs):
        self.context = kwargs.get("context", {})

    def to_representation(self, instance):
        return instance


@pytest.fixture
def mock_request():
    mock_req = MagicMock()
    mock_req.group_permissions = [MagicMock()]
    return mock_req

@pytest.fixture
def mock_serializer(mock_request):
    @serializer_permissions()
    class WrappedSerializer(MockSerializer):
        pass

    return WrappedSerializer(context={"request": mock_request})


def test_serializer_permissions_non_private_api(mock_serializer):
    with patch.dict(os.environ, {"PRIVATE_API_INSTANCE": "0"}):
        serializer = mock_serializer
        result = serializer.to_representation(core_headline_data)
        assert "is_private" not in result, "is_private should be removed"
        assert result == core_headline_data, "all fields should be returned"


@pytest.mark.parametrize(
    "action1,action2,action3,is_private,expected",
    [
        (True, True, True, True, True),
    ]
)
def test_serializer_permissions_private_api_with_match(mock_serializer, action1, action2, action3, is_private, expected):
    with patch.dict(os.environ, {"PRIVATE_API_INSTANCE": "1"}):
        serializer = mock_serializer

        test_data = copy.deepcopy(core_headline_data)

        with patch("metrics.utils.auth_action.MatchThemeSubthemeAction.execute") as mock_theme, \
            patch("metrics.utils.auth_action.MatchTopLevelFieldsAction.execute") as mock_top, \
            patch("metrics.utils.auth_action.MatchFieldAction.execute") as mock_field, \
            patch("metrics.utils.auth_action.ValidationAction.execute") as mock_validation:

            mock_theme.return_value = action1
            mock_top.return_value = action2
            mock_field.return_value = action3

            mock_validation.return_value = None
            mock_validation.did_match = True

            result = serializer.to_representation(test_data)
            if expected:
                assert result == test_data, "all fields should be returned"
                assert "is_private" not in result, "is_private should be removed"
            else:
                assert result is None, "result should be None when permissions do not match"
