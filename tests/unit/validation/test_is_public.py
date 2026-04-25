import pytest
from unittest import mock

from validation.is_public import (
    FILE_AND_DATA_IS_PUBLIC_MISMATCH_ERROR,
    IS_PUBLIC_BOOLEAN_ERROR,
    METRIC_AND_DATA_IS_PUBLIC_MISMATCH_ERROR,
    MISSING_IS_PUBLIC_FIELD_ERROR,
    MIXED_IS_PUBLIC_VALUES_ERROR,
    NON_PUBLIC_DATA_PREFIX,
    NOT_METRIC_ERROR,
    validate_is_public,
)


class TestValidateIsPublicStatus:
    PUBLIC_METRIC = "RSV_headline_positivityLatest"
    NON_PUBLIC_METRIC = f"{NON_PUBLIC_DATA_PREFIX}{PUBLIC_METRIC}"
    PUBLIC_FILENAME = f"{PUBLIC_METRIC}.json"
    NON_PUBLIC_FILENAME = f"{NON_PUBLIC_METRIC}.json"

    def test_allows_public_source_data_when_metric_and_filename_are_public(self):
        validate_is_public(
            source_data={"metric": self.PUBLIC_METRIC},
            fields=[{"is_public": True}, {"is_public": True}],
            filename=self.PUBLIC_FILENAME,
        )

    def test_allows_non_public_source_data_when_metric_and_filename_are_non_public(
        self,
    ):
        validate_is_public(
            source_data={"metric": self.NON_PUBLIC_METRIC},
            fields=[{"is_public": False}, {"is_public": False}],
            filename=self.NON_PUBLIC_FILENAME,
        )

    def test_allows_public_source_data_when_fields_is_an_empty_list(self):
        validate_is_public(
            source_data={"metric": self.PUBLIC_METRIC},
            fields=[],
            filename=self.PUBLIC_FILENAME,
        )

    def test_allows_non_public_source_data_when_fields_is_an_empty_list(self):
        validate_is_public(
            source_data={"metric": self.NON_PUBLIC_METRIC},
            fields=[],
            filename=self.NON_PUBLIC_FILENAME,
        )

    def test_allows_public_source_data_when_fields_is_an_empty_tuple(self):
        validate_is_public(
            source_data={"metric": self.PUBLIC_METRIC},
            fields=(),
            filename=self.PUBLIC_FILENAME,
        )

    def test_allows_non_public_source_data_when_fields_is_an_empty_tuple(self):
        validate_is_public(
            source_data={"metric": self.NON_PUBLIC_METRIC},
            fields=(),
            filename=self.NON_PUBLIC_FILENAME,
        )

    def test_raises_error_when_non_public_metric_prefix_does_not_match_public_filename(
        self,
    ):
        with pytest.raises(ValueError) as exc_info:
            validate_is_public(
                source_data={"metric": self.NON_PUBLIC_METRIC},
                fields=[{"is_public": False}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == FILE_AND_DATA_IS_PUBLIC_MISMATCH_ERROR

    def test_raises_error_when_public_metric_prefix_does_not_match_non_public_filename(
        self,
    ):
        with pytest.raises(ValueError) as exc_info:
            validate_is_public(
                source_data={"metric": self.PUBLIC_METRIC},
                fields=[{"is_public": True}],
                filename=self.NON_PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == FILE_AND_DATA_IS_PUBLIC_MISMATCH_ERROR

    @mock.patch("validation.is_public.ALLOW_MISSING_IS_PUBLIC_FIELD", False)
    def test_raises_error_when_is_public_field_is_missing(self):
        with pytest.raises(ValueError) as exc_info:
            validate_is_public(
                source_data={"metric": self.PUBLIC_METRIC},
                fields=[{"period_start": "2023-10-23"}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == MISSING_IS_PUBLIC_FIELD_ERROR

    @mock.patch("validation.is_public.ALLOW_MISSING_IS_PUBLIC_FIELD", True)
    def test_logs_when_is_public_field_is_missing_and_flag_allows_it(self):
        with mock.patch("validation.is_public.logger") as mock_logger:
            validate_is_public(
                source_data={"metric": self.PUBLIC_METRIC},
                fields=[{"period_start": "2023-10-23"}],
                filename=self.PUBLIC_FILENAME,
            )

        mock_logger.info.assert_called_once_with(
            "Missing is_public field in %s", self.PUBLIC_FILENAME
        )

    def test_raises_error_when_is_public_value_is_not_boolean(self):
        with pytest.raises(TypeError) as exc_info:
            validate_is_public(
                source_data={"metric": self.PUBLIC_METRIC},
                fields=[{"is_public": "true"}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == IS_PUBLIC_BOOLEAN_ERROR

    def test_raises_error_when_data_fields_mix_public_and_non_public_values(self):
        with pytest.raises(ValueError) as exc_info:
            validate_is_public(
                source_data={"metric": self.PUBLIC_METRIC},
                fields=[{"is_public": True}, {"is_public": False}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == MIXED_IS_PUBLIC_VALUES_ERROR

    def test_raises_error_when_non_public_metric_prefix_does_not_match_public_is_public(
        self,
    ):
        with pytest.raises(ValueError) as exc_info:
            validate_is_public(
                source_data={"metric": self.NON_PUBLIC_METRIC},
                fields=[{"is_public": True}],
                filename=self.NON_PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == METRIC_AND_DATA_IS_PUBLIC_MISMATCH_ERROR

    def test_raises_error_when_public_metric_prefix_does_not_match_non_public_is_public(
        self,
    ):
        with pytest.raises(ValueError) as exc_info:
            validate_is_public(
                source_data={"metric": self.PUBLIC_METRIC},
                fields=[{"is_public": False}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == METRIC_AND_DATA_IS_PUBLIC_MISMATCH_ERROR

    def test_raises_error_when_metric_is_missing(self):
        with pytest.raises(TypeError) as exc_info:
            validate_is_public(
                source_data={},
                fields=[{"is_public": True}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == NOT_METRIC_ERROR

    def test_raises_error_when_metric_is_none(self):
        with pytest.raises(TypeError) as exc_info:
            validate_is_public(
                source_data={"metric": None},
                fields=[{"is_public": True}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == NOT_METRIC_ERROR

    def test_raises_error_when_metric_is_not_a_string(self):
        with pytest.raises(TypeError) as exc_info:
            validate_is_public(
                source_data={"metric": 123},
                fields=[{"is_public": True}],
                filename=self.PUBLIC_FILENAME,
            )

        assert str(exc_info.value) == NOT_METRIC_ERROR
