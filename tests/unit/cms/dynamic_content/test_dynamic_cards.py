import json
from django import forms
import unittest
from unittest import mock
from wagtail.blocks.struct_block import StructBlockAdapter

import pytest

from cms.dynamic_content.dynamic_cards import (
    get_all_subcategory_choices,
    DualCategoryChartCard,
    DualCategoryChartCardAdapter,
)
from cms.metrics_interface import interface, field_choices_callables

MOCK_SUBCATEGORY_CHOICES_DB = {
    "age": ["00-04", "05-11"],
    "sex": ["m", "f"],
    "stratum": ["default", "unknown"],
    "geography": ["Enfield", "Waverley"],
}


class TestGetAllSubcategoryChoices:
    @mock.patch(
        "cms.dynamic_content.dynamic_cards.SUBCATEGORY_CHOICES_DB",
        MOCK_SUBCATEGORY_CHOICES_DB,
    )
    def test_get_all_subcategory_choices(self):
        """
        Given a a mocked `SUBCATEGORY_CHOICES_DB`
        When `get_all_subcategory_choices` is called
        Then the expected subcategory choices are returned.
        """
        # Given
        mock_subcategory_choices_flat = [
            item for items in MOCK_SUBCATEGORY_CHOICES_DB.values() for item in items
        ]

        # When
        received_all_subcategory_choices = get_all_subcategory_choices()

        # Then
        assert received_all_subcategory_choices == mock_subcategory_choices_flat


class TestDualCategoryChartCard:
    @pytest.mark.parametrize(
        "expected_dual_chart_card_field_name",
        (
            "title",
            "body",
            "about",
            "tag_manager_event_id",
            "x_axis",
            "x_axis_title",
            "primary_field_values",
            "y_axis",
            "y_axis_title",
            "y_axis_minimum_value",
            "y_axis_maximum_value",
            "chart_type",
            "second_category",
        ),
    )
    def test_dual_chart_card_has_expected_fields(
        self, expected_dual_chart_card_field_name: str
    ):
        """
        Given an instance of `DualCategoryChartCard`
        When inspecting child blocks
        Then The expected field(s) are available
        """
        # Given
        dual_category_chart_card = DualCategoryChartCard()

        # When
        selected_field = dual_category_chart_card.child_blocks.get(
            expected_dual_chart_card_field_name
        )

        # Then
        assert selected_field is not None

    @mock.patch(
        "cms.dynamic_content.dynamic_cards.SUBCATEGORY_CHOICES_DB",
        MOCK_SUBCATEGORY_CHOICES_DB,
    )
    def test_get_form_context_with_default_parameters(self):
        """
        Given an instance of `DualCategoryChartCard`
        When `get_form_context()` is called
        Then the expected `prefix` and `subcategory_data` is available
        """
        # Given
        mock_value = {}
        mock_prefix = "mock-prefix"
        dual_category_chart_card = DualCategoryChartCard()
        expected_context_subcategory_data = json.dumps(MOCK_SUBCATEGORY_CHOICES_DB)

        # When
        context = dual_category_chart_card.get_form_context(
            mock_value,
            mock_prefix,
        )

        # Then
        assert context["prefix"] == mock_prefix
        assert context["subcategory_data"] == expected_context_subcategory_data


class TestDualCategoryChartCardAdapter:
    def test_js_constructor_is_set_correctly(self):
        """
        Given a DualCategoryChartAdapter instance
        When accessing the js_constructor property
        Then it returns the correct javascript constructor name
        """
        # Given
        dual_chart_adapter = DualCategoryChartCardAdapter()
        expected_js_constructor = (
            "cms.dynamic_content.dynamic_cards.DualCategoryChartCard"
        )

        # When
        received_js_constructor = dual_chart_adapter.js_constructor

        # Then
        assert received_js_constructor == expected_js_constructor

    @mock.patch.object(StructBlockAdapter, "media", forms.Media(js=["mock_parent.js"]))
    def test_media_preserves_parent_js_unchanged(self):
        """
        Given a DualCategoryChartAdapter instance and mocked parent media with existing js
        When accessing the media property
        Then it combines parent JS files where `dual_category_chart_form.js`
        """
        # Given
        dual_chart_adapter = DualCategoryChartCardAdapter()
        expected_media_js = ["mock_parent.js", "js/dual_category_chart_form.js"]

        # When
        dual_chart_adapter_media = dual_chart_adapter.media

        # Then
        assert dual_chart_adapter_media._js == expected_media_js
