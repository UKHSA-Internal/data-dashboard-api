from unittest.mock import MagicMock, patch
from django import forms
from unittest import mock
import pytest
from django.core.exceptions import ObjectDoesNotExist
from wagtail.blocks import StructBlock, StructBlockValidationError, StructValue
from wagtail.blocks.struct_block import StructBlockAdapter

from cms.dynamic_content.components import HeadlineNumberComponent
from cms.dynamic_content.elements import BaseMetricsElement, BaseMetricsElementAdapter
from cms.metrics_interface import MetricsAPIInterface


class TestValidateMetricGroup:

    @pytest.mark.parametrize(
        "metric, expected_group",
        [
            ("covid-19_testing_count", "testing"),
            ("OFF-SENS_influenza_headline_positivityLatest", "headline"),
            ("OFF-SENS_MMR1_coverage_coverageByYear", "coverage"),
        ],
    )
    def test_successful_extraction(self, metric: str, expected_group: str):
        """
        Given a valid metric value in a block
        When `_validate_metric_group()` is called
        Then no errors are produced and the group is returned
        """
        # given
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value={"metric": metric})

        # when
        group = BaseMetricsElement._validate_metric_group(value=value)

        # then
        assert group == expected_group

    def test_unsuccessful_extraction(self):
        """
        Given an invalid metric value in a block
        When `_validate_metric_group()` is called
        Then a StructBlockValidationError error is raised
        """
        # given
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value={"metric": "not-a-valid-value"})

        # when
        with pytest.raises(StructBlockValidationError) as exc_info:
            BaseMetricsElement._validate_metric_group(value=value)

        # then
        block_errors = exc_info.value.block_errors
        assert (
            block_errors["metric"].message == "Invalid metric, could not extract group"
        )


class TestValidateGeographyCode:

    @patch.object(MetricsAPIInterface, "get_geography_code_for_geography")
    def test_valid_combination(
        self, mocked_get_geography_code_for_geography: MagicMock
    ):
        """
        Given a valid geography and geography_type combination in a block
        When `_validate_geography_code()` is called
        Then no errors are produced and the geography code is returned
        """
        # given
        mocked_get_geography_code_for_geography.return_value = "E92000001"
        block = BaseMetricsElement()
        value: StructValue = block.to_python(
            value={
                "geography": "England",
                "geography_type": "Nation",
            }
        )

        # when
        code = BaseMetricsElement._validate_geography_code(value=value)

        # then
        assert code == "E92000001"

    @patch.object(MetricsAPIInterface, "get_geography_code_for_geography")
    def test_invalid_combination(
        self, mocked_get_geography_code_for_geography: MagicMock
    ):
        """
        Given an invalid geography and geography_type combination in a block value
        When `_validate_geography_code()` is called
        Then a StructBlockValidationError error is raised
        """
        # given
        mocked_get_geography_code_for_geography.side_effect = ObjectDoesNotExist()
        block = BaseMetricsElement()
        value: StructValue = block.to_python(
            value={
                "geography": "England",
                "geography_type": "Lower Tier Local Authority",
            }
        )

        # when
        with pytest.raises(StructBlockValidationError) as exc_info:
            BaseMetricsElement._validate_geography_code(value=value)

        # then
        block_errors = exc_info.value.block_errors
        assert (
            block_errors["geography_type"].message
            == "Geography type does not match geography"
        )


class TestBaseMetricsElementClean:

    @property
    def valid_payload(self) -> dict[str, str]:
        """
        A valid basic block payload for all tests to use.
        """
        return {
            "theme": "infectious_disease",
            "sub_theme": "respiratory",
            "topic": "Adenovirus",
            "metric": "adenovirus_testing_positivityByWeek",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "age": "all",
            "stratum": "default",
        }

    @patch.object(StructBlock, "clean")
    @patch.object(MetricsAPIInterface, "get_geography_code_for_geography")
    def test_valid_struct(
        self,
        mocked_get_geography_code_for_geography: MagicMock,
        mocked_super_clean: MagicMock,
    ):
        """
        Given a valid combination of field values
        When `clean()` is called
        Then no errors are produced and the super clean method is called

        Patches:
            `mocked_get_geography_code_for_geography` to produce a valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
        """
        # given
        mocked_get_geography_code_for_geography.return_value = "E92000001"
        # use a subclass of the base block to test a real scenario and ensure the
        # underlying IncomingBaseDataModel correctly handles additional parameters it
        # isn't expecting (e.g. the body field value in this example)
        block = HeadlineNumberComponent()
        value: StructValue = block.to_python(
            # add the necessary additional field value the HeadlineNumberComponent needs
            value={**self.valid_payload, "body": "Test body"}
        )
        mocked_super_clean.return_value = value

        # when
        block.clean(value=value)

        # then
        mocked_super_clean.assert_called_once_with(value=value)
        mocked_get_geography_code_for_geography.assert_called_once()

    @patch.object(StructBlock, "clean")
    @patch("cms.dynamic_content.elements.IncomingBaseDataModel")
    @patch.object(MetricsAPIInterface, "get_geography_code_for_geography")
    def test_metric_group_and_geography_code_passed_correctly(
        self,
        mocked_get_geography_code_for_geography: MagicMock,
        mocked_incoming_base_data_model: MagicMock,
        mocked_super_clean: MagicMock,
    ):
        """
        Given a valid metric name
        When `clean()` is called
        Then the metric group extracted from the metric name is passed to the
        IncomingBaseDataModel correctly as is the geography code

        Patches:
            `mocked_get_geography_code_for_geography` to produce a valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
            `mocked_incoming_base_data_model` patches the IncomingBaseDataModel so that
            we can sniff the parameters passed to it
        """
        # given
        mocked_get_geography_code_for_geography.return_value = "E92000001"
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value=self.valid_payload)
        mocked_super_clean.return_value = value

        # when
        block.clean(value=value)

        # then
        mocked_incoming_base_data_model.assert_called_once_with(
            **self.valid_payload,
            geography_code="E92000001",
            metric_group="testing",
        )

    @patch.object(StructBlock, "clean")
    @patch.object(MetricsAPIInterface, "get_geography_code_for_geography")
    def test_error_messages(
        self,
        mocked_get_geography_code_for_geography: MagicMock,
        mocked_super_clean: MagicMock,
    ):
        """
        Given an invalid block value
        When `clean()` is called
        Then the correct errors are produced

        Patches:
            `mocked_get_geography_code_for_geography` to produce a valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
        """
        # given
        mocked_get_geography_code_for_geography.return_value = "E92000001"
        invalid_payload = {
            **self.valid_payload,
            # replace the topic and the age with invalid values
            "topic": "not-a-topic",
            "age": "not-an-age",
        }
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value=invalid_payload)
        mocked_super_clean.return_value = value

        # when
        with pytest.raises(StructBlockValidationError) as exc_info:
            block.clean(value=value)

        # then
        block_errors = exc_info.value.block_errors
        # check no other errors come through other than the ones we expect
        assert len(block_errors) == 2
        # the error is against the metric field here not the topic as the
        # validation is done on the metric field in the model
        assert "metric" in block_errors
        assert "age" in block_errors


class TestBaseMetricsElementAdapter:
    def test_js_constructor_is_set_correctly(self):
        """
        Given a BaseMetricsElementAdapter instance
        When accessing the js_constructor property
        Then it returns the correct javascript constructor name
        """
        # Given
        adapter = BaseMetricsElementAdapter()
        expected_js_constructor = "cms.dynamic_content.elements.BaseMetricsElement"

        # When
        received_js_constructor = adapter.js_constructor

        # Then
        assert received_js_constructor == expected_js_constructor

    @mock.patch.object(
        StructBlockAdapter,
        "media",
        forms.Media(js=["mock_parent.js"]),
    )
    def test_media_preserves_parent_js_unchanged(self):
        """
        Given a BaseMetricsElementAdapter instance and mocked parent media with existing js
        When accessing the media property
        Then it combines parent JS files with metric_dropdown_manager.js
        """
        # Given
        adapter = BaseMetricsElementAdapter()
        expected_media_js = [
            "mock_parent.js",
            "js/metric_dropdown_manager.js",
        ]

        # When
        adapter_media = adapter.media

        # Then
        assert adapter_media._js == expected_media_js
