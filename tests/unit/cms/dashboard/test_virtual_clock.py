import datetime
from unittest import mock

import pytest

from common import virtual_clock


@pytest.fixture(autouse=True)
def clear_virtual_clock_context():
    virtual_clock.clear_embargo_time()
    yield
    virtual_clock.clear_embargo_time()


class TestParseEmbargoTimeValue:
    @mock.patch("common.virtual_clock.timezone.now")
    def test_returns_now_for_now_string(self, spy_now: mock.MagicMock):
        """
        Given an embargo time value of now
        When parse_embargo_time_value is called
        Then the current timezone-aware datetime is returned
        """
        expected = datetime.datetime(2026, 3, 31, 12, 0, tzinfo=datetime.UTC)
        spy_now.return_value = expected

        actual = virtual_clock.parse_embargo_time_value(" now ")

        assert actual == expected

    @pytest.mark.parametrize(
        "embargo_time_value,expected_epoch",
        [
            (1711456200, 1711456200),
            (1711456200.9, 1711456200),
            ("1711456200", 1711456200),
        ],
    )
    def test_accepts_numeric_epoch_values(self, embargo_time_value, expected_epoch):
        """
        Given a numeric embargo time value
        When parse_embargo_time_value is called
        Then the corresponding UTC datetime is returned
        """
        actual = virtual_clock.parse_embargo_time_value(embargo_time_value)

        assert actual == datetime.datetime.fromtimestamp(
            expected_epoch, tz=datetime.UTC
        )

    @pytest.mark.parametrize("embargo_time_value", [True, False, object()])
    def test_returns_none_for_unsupported_value_types(self, embargo_time_value):
        """
        Given an unsupported embargo time value type
        When parse_embargo_time_value is called
        Then None is returned
        """
        assert virtual_clock.parse_embargo_time_value(embargo_time_value) is None

    def test_boo(self):
        """
        Given an epoch value that cannot be converted to a datetime
        When parse_embargo_time_value is called
        Then None is returned
        """

        result = virtual_clock.parse_embargo_time_value("1711456200")
        assert isinstance(result, datetime.datetime)

    @mock.patch("common.virtual_clock.datetime")
    def test_returns_none_when_timestamp_cannot_be_converted(
        self, spy_datetime_class: mock.MagicMock
    ):
        """
        Given an epoch value that cannot be converted to a datetime
        When parse_embargo_time_value is called
        Then None is returned
        """
        spy_datetime_class.fromtimestamp.side_effect = OverflowError

        assert virtual_clock.parse_embargo_time_value("1711456200") is None
        spy_datetime_class.fromtimestamp.assert_called_once_with(1711456200)


class TestSetEmbargoTime:
    @mock.patch("common.virtual_clock._logger.error")
    @mock.patch("common.virtual_clock.timezone.now")
    def test_raises_when_page_previews_are_disabled(
        self,
        spy_now: mock.MagicMock,
        spy_logger_error: mock.MagicMock,
        settings,
    ):
        """
        Given page previews are disabled
        When set_embargo_time is called
        Then an Embargo Date not supported error is raised and the current time is stored
        """
        expected = datetime.datetime(2026, 3, 31, 12, 0, tzinfo=datetime.UTC)
        spy_now.return_value = expected
        settings.PAGE_PREVIEWS_ENABLED = False

        with pytest.raises(virtual_clock.EmbargoDateNotSupportedError):
            virtual_clock.set_embargo_time(embargo_time_value="now", token="token")

        assert virtual_clock.get_embargo_time() == expected
        spy_logger_error.assert_called_once_with(
            virtual_clock.EMBARGO_DATE_NOT_SUPPORTED_MESSAGE
        )

    @mock.patch("common.virtual_clock.validate_preview_hmac_token", return_value=False)
    def test_returns_false_for_invalid_token(
        self, spy_validate_preview_hmac_token: mock.MagicMock, settings
    ):
        """
        Given page previews are enabled and the preview token is invalid
        When set_embargo_time is called
        Then False is returned
        """
        settings.PAGE_PREVIEWS_ENABLED = True

        actual = virtual_clock.set_embargo_time(embargo_time_value="now", token="token")

        assert actual is False
        spy_validate_preview_hmac_token.assert_called_once_with("token")

    @mock.patch("common.virtual_clock.validate_preview_hmac_token", return_value=True)
    def test_returns_false_for_unparseable_embargo_time(
        self, spy_validate_preview_hmac_token: mock.MagicMock, settings
    ):
        """
        Given page previews are enabled and the token is valid
        When set_embargo_time is called with an unparseable value
        Then False is returned
        """
        settings.PAGE_PREVIEWS_ENABLED = True

        actual = virtual_clock.set_embargo_time(
            embargo_time_value="not-a-time", token="token"
        )

        assert actual is False
        spy_validate_preview_hmac_token.assert_called_once_with("token")

    @mock.patch("common.virtual_clock.validate_preview_hmac_token", return_value=True)
    def test_sets_embargo_time_for_valid_value(
        self, spy_validate_preview_hmac_token: mock.MagicMock, settings
    ):
        """
        Given page previews are enabled and the token is valid
        When set_embargo_time is called with a valid epoch value
        Then the embargo time is stored for the current context
        """
        settings.PAGE_PREVIEWS_ENABLED = True
        expected = datetime.datetime.fromtimestamp(1711456200, tz=datetime.UTC)

        actual = virtual_clock.set_embargo_time(
            embargo_time_value="1711456200", token="token"
        )

        assert actual is True
        assert virtual_clock.get_embargo_time() == expected
        spy_validate_preview_hmac_token.assert_called_once_with("token")


class TestGetAndClearEmbargoTime:
    @mock.patch("common.virtual_clock.timezone.now")
    def test_get_embargo_time_falls_back_to_now_after_clear(
        self, spy_now: mock.MagicMock
    ):
        """
        Given a previously set embargo time that has been cleared
        When get_embargo_time is called
        Then the current timezone-aware datetime is returned
        """
        stored = datetime.datetime.fromtimestamp(1711456200, tz=datetime.UTC)
        fallback = datetime.datetime(2026, 4, 1, 9, 30, tzinfo=datetime.UTC)
        virtual_clock._embargo_time_ctx.set(stored)
        virtual_clock.clear_embargo_time()
        spy_now.return_value = fallback

        actual = virtual_clock.get_embargo_time()

        assert actual == fallback
