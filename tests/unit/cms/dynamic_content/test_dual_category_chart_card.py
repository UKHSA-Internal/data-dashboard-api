import json
from django import forms
from unittest import mock
from wagtail.blocks.struct_block import StructBlockAdapter

import pytest

from cms.dynamic_content.cards import (
    DualCategoryChartCard,
    DualCategoryChartCardAdapter,
)
from cms.metrics_interface import field_choices_callables


class TestDualCategoryChartCard:
    @mock.patch.object(
        field_choices_callables, "get_all_geography_choices_grouped_by_type"
    )
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
        self,
        mocked_get_all_geography_choices_grouped_by_type: mock.MagicMock,
        expected_dual_chart_card_field_name: str,
        fake_subcategory_choices_grouped_by_categories: dict[str, list[str]],
    ):
        """
        Given an instance of `DualCategoryChartCard`
        When inspecting child blocks
        Then The expected field(s) are available
        """
        # Given
        mocked_get_all_geography_choices_grouped_by_type.return_value = (
            fake_subcategory_choices_grouped_by_categories["geography"]
        )
        dual_category_chart_card = DualCategoryChartCard()

        # When
        selected_field = dual_category_chart_card.child_blocks.get(
            expected_dual_chart_card_field_name
        )

        # Then
        assert selected_field is not None

    @mock.patch(
        "cms.dynamic_content.cards.get_all_subcategory_choices_grouped_by_categories"
    )
    def test_get_form_context_with_default_parameters(
        self,
        mocked_get_subcategory_choices_grouped_by_categories: mock.MagicMock,
        fake_subcategory_choices_grouped_by_categories: dict[str, list[str]],
    ):
        """
        Given an instance of `DualCategoryChartCard`
        When `get_form_context()` is called
        Then the expected `prefix` and `subcategory_data` is available
        """
        # Given
        mock_value = {}
        mock_prefix = "mock-prefix"
        fake_subcategory_choices = fake_subcategory_choices_grouped_by_categories
        mocked_get_subcategory_choices_grouped_by_categories.return_value = (
            fake_subcategory_choices
        )
        dual_category_chart_card = DualCategoryChartCard()
        expected_context_subcategory_data = json.dumps(fake_subcategory_choices)

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
        expected_js_constructor = "cms.dynamic_content.cards.DualCategoryChartCard"

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
