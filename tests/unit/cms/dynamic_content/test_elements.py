from functools import wraps
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist
from wagtail.blocks import StructBlock, StructBlockValidationError, StructValue

from cms.dynamic_content.components import HeadlineNumberComponent
from cms.dynamic_content.elements import BaseMetricsElement
from cms.metrics_interface import MetricsAPIInterface


def with_geography_code(code: str = "E92000001") -> Callable:
    """
    Decorator which patches the MetricsAPIInterface's get_geography_code_for_geography
    method to a specific value for the duration of the wrapped function.

    Args:
        code: The geography code to return when the interface method is called
    """

    def run_with_patch(func: Callable) -> Callable:
        @wraps(func)
        def run(*args, **kwargs):
            with patch.object(
                MetricsAPIInterface, "get_geography_code_for_geography"
            ) as mocked_get_geography_code_for_geography:
                mocked_get_geography_code_for_geography.return_value = code
                func(*args, **kwargs)

        return run

    return run_with_patch


class TestBaseMetricsElementClean:

    @property
    def valid_payload(self) -> dict[str, str]:
        """
        A valid basic block payload for all tests to use.
        """
        return {
            "topic": "Adenovirus",
            "metric": "adenovirus_testing_positivityByWeek",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "age": "all",
            "stratum": "default",
        }

    @patch.object(StructBlock, "clean")
    @with_geography_code()
    def test_valid_struct(self, mocked_super_clean: MagicMock):
        """
        Given a valid combination of field values
        When `clean()` is called
        Then no errors are produced and the super clean method is called

        Patches:
            `get_geography_code_for_geography` via `with_geography_code` to produce a
            valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
        """
        # given
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

    @patch.object(StructBlock, "clean")
    @with_geography_code()
    def test_metric_group_extraction_failure(self, mocked_super_clean: MagicMock):
        """
        Given an invalid metric name
        When `clean()` is called
        Then an error is produced indicating the metric group couldn't be extracted

        Patches:
            `get_geography_code_for_geography` via `with_geography_code` to produce a
            valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
        """
        # given
        # override the metric with an invalid one
        payload = {**self.valid_payload, "metric": "covid-19_the-group"}
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value=payload)
        mocked_super_clean.return_value = value

        # when
        with pytest.raises(StructBlockValidationError) as exc_info:
            block.clean(value=value)

        # then
        mocked_super_clean.assert_called_once()
        block_errors = exc_info.value.block_errors
        assert (
            block_errors["metric"].message == "Invalid metric, could not extract group"
        )

    @patch.object(StructBlock, "clean")
    @patch("cms.dynamic_content.elements.IncomingBaseDataModel")
    @with_geography_code()
    def test_metric_group_passed_correctly(
        self, mocked_incoming_base_data_model: MagicMock, mocked_super_clean: MagicMock
    ):
        """
        Given a valid metric name
        When `clean()` is called
        Then the metric group extracted from the metric name is passed to the
        IncomingBaseDataModel correctly

        Patches:
            `get_geography_code_for_geography` via `with_geography_code` to produce a
            valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
            `mocked_incoming_base_data_model` patches the IncomingBaseDataModel so that
            we can sniff the parameters passed to it
        """
        # given
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value=self.valid_payload)
        mocked_super_clean.return_value = value
        # use the patched get_geography_code_for_geography method to get the expected
        # geography code - we're not really testing this, just need this value to make
        # our call assertion at the end neater
        expected_geography_code = (
            MetricsAPIInterface().get_geography_code_for_geography(
                self.valid_payload["geography"], self.valid_payload["geography_type"]
            )
        )

        # when
        block.clean(value=value)

        # then
        mocked_incoming_base_data_model.assert_called_once_with(
            **self.valid_payload,
            geography_code=expected_geography_code,
            metric_group="testing",
        )

    @patch.object(StructBlock, "clean")
    @with_geography_code()
    def test_error_messages(self, mocked_super_clean: MagicMock):
        """
        Given an invalid block value
        When `clean()` is called
        Then the correct errors are produced

        Patches:
            `get_geography_code_for_geography` via `with_geography_code` to produce a
            valid geography code
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
        """
        # given
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

    @patch.object(StructBlock, "clean")
    @patch.object(MetricsAPIInterface, "get_geography_code_for_geography")
    def test_error_messages_geography(
        self,
        mocked_get_geography_code_for_geography: MagicMock,
        mocked_super_clean: MagicMock,
    ):
        """
        Given an invalid geography combination
        When `clean()` is called
        Then an error is produced

        Patches:
            `mocked_get_geography_code_for_geography` patches the interface's
            `get_geography_code_for_geography` method allowing us to return an error
            `mocked_super_clean` patches the StructBlock's clean method so that we don't
            have to use the database and seed it with data that would allow the base
            field's checks to pass
        """
        # given
        mocked_get_geography_code_for_geography.side_effect = ObjectDoesNotExist
        block = BaseMetricsElement()
        value: StructValue = block.to_python(value=self.valid_payload)
        mocked_super_clean.return_value = value

        # when
        with pytest.raises(StructBlockValidationError) as exc_info:
            block.clean(value=value)

        # then
        block_errors = exc_info.value.block_errors
        # check no other errors come through other than the ones we expect
        assert len(block_errors) == 1
        assert (
            block_errors["geography_type"].message
            == "Geography type does not match geography"
        )
