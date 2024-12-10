from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from botocore.exceptions import ClientError
from django.core.mail import EmailMessage

from feedback.email_server import (
    DEFAULT_FEEDBACK_EMAIL_SUBJECT,
    create_email_message,
    send_email,
    create_email_message_v2,
    send_email_v2,
    send_email_via_ses,
)

MODULE_PATH = "feedback.email_server"


class TestCreateEmailMessage:
    fake_recipient_email_address = "not.real@test.com"

    def test_returns_email_message(self):
        """
        Given a suggestions dict and a recipient email address
        When `create_email_message()` is called
        Then an instance of `EmailMessage` is returned
        """
        # Given
        mocked_suggestions = mock.MagicMock()
        fake_subject = "Test subject"

        # When
        email_message: EmailMessage = create_email_message(
            suggestions=mocked_suggestions,
            subject=fake_subject,
            recipient_email_address=self.fake_recipient_email_address,
        )

        # Then
        assert type(email_message) is EmailMessage

    @mock.patch(f"{MODULE_PATH}.build_body_for_email")
    def test_sets_correct_body_on_email_message(
        self, spy_build_body_for_email: mock.MagicMock
    ):
        """
        Given a suggestions dict and a recipient email address
        When `create_email_message()` is called
        The body is set by delegating a call to `build_body_for_email()`

        Patches:
            `spy_build_body_for_email`: For the main assertion.
                To check this is used for the `body`
                of the created `EmailMessage`
        """
        # Given
        mocked_suggestions = mock.Mock()
        fake_subject = "Test subject"

        # When
        email_message: EmailMessage = create_email_message(
            suggestions=mocked_suggestions,
            subject=fake_subject,
            recipient_email_address=self.fake_recipient_email_address,
        )

        # Then
        spy_build_body_for_email.assert_called_once_with(suggestions=mocked_suggestions)
        assert email_message.body == spy_build_body_for_email.return_value

    def test_sets_default_subject_on_email_message_when_not_provided(self):
        """
        Given a suggestions dict and a recipient email address
        When `create_email_message()` is called
        Then the default subject line is set on the email message
        """
        # Given
        mocked_suggestions = mock.MagicMock()

        # When
        email_message: EmailMessage = create_email_message(
            suggestions=mocked_suggestions,
            recipient_email_address=self.fake_recipient_email_address,
        )

        # Then
        assert email_message.subject == DEFAULT_FEEDBACK_EMAIL_SUBJECT

    def test_sets_specified_subject_on_email_message_when_provided(self):
        """
        Given a suggestions dict and a recipient email address
        And a specified non-default subject line
        When `create_email_message()` is called
        Then the specified subject line is set on the email message
        """
        # Given
        mocked_suggestions = mock.MagicMock()
        fake_non_default_subject = "Specified example subject"

        # When
        email_message: EmailMessage = create_email_message(
            suggestions=mocked_suggestions,
            recipient_email_address=self.fake_recipient_email_address,
            subject=fake_non_default_subject,
        )

        # Then
        assert email_message.subject == fake_non_default_subject

    def test_sets_specified_recipient_on_email_message_when_provided(self):
        """
        Given a suggestions dict and a specified recipient email address
        When `create_email_message()` is called
        Then the specified recipient is set on the recipients of the email message
        """
        # Given
        mocked_suggestions = mock.MagicMock()
        fake_non_default_subject = "Specified example subject"

        # When
        email_message: EmailMessage = create_email_message(
            suggestions=mocked_suggestions,
            recipient_email_address=self.fake_recipient_email_address,
            subject=fake_non_default_subject,
        )

        # Then
        assert self.fake_recipient_email_address in email_message.recipients()


class TestCreateEmailMessageV2:
    fake_recipient_email_address = "not.real@test.com"

    @mock.patch(f"{MODULE_PATH}.build_body_for_email_v2")
    def test_returns_email_message(
        self, mocked_build_body_for_email_v2: mock.MagicMock
    ):
        """
        Given a suggestions dict and a recipient email address
        When `create_email_message()` is called
        Then an instance of `EmailMessage` is returned
        """
        # Given
        mocked_suggestions = mock.MagicMock()
        fake_subject = "Test subject"

        # When
        email_message: EmailMessage = create_email_message_v2(
            suggestions=mocked_suggestions,
            subject=fake_subject,
            recipient_email_address=self.fake_recipient_email_address,
        )

        # Then
        assert type(email_message) is EmailMessage

    @mock.patch(f"{MODULE_PATH}.build_body_for_email_v2")
    def test_sets_correct_body_on_email_message(
        self, spy_build_body_for_email: mock.MagicMock
    ):
        """
        Given a suggestions dict and a recipient email address
        When `create_email_message()` is called
        The body is set by delegating a call to `build_body_for_email()`

        Patches:
            `spy_build_body_for_email`: For the main assertion.
                To check this is used for the `body`
                of the created `EmailMessage`
        """
        # Given
        mocked_suggestions = mock.Mock()
        fake_subject = "Test subject"

        # When
        email_message: EmailMessage = create_email_message_v2(
            suggestions=mocked_suggestions,
            subject=fake_subject,
            recipient_email_address=self.fake_recipient_email_address,
        )

        # Then
        spy_build_body_for_email.assert_called_once_with(suggestions=mocked_suggestions)
        assert email_message.body == spy_build_body_for_email.return_value

    @mock.patch(f"{MODULE_PATH}.build_body_for_email_v2")
    def test_sets_default_subject_on_email_message_when_not_provided(
        self, mocked_build_body_for_email_v2: mock.MagicMock
    ):
        """
        Given a suggestions dict and a recipient email address
        When `create_email_message()` is called
        Then the default subject line is set on the email message
        """
        # Given
        mocked_suggestions = mock.MagicMock()

        # When
        email_message: EmailMessage = create_email_message_v2(
            suggestions=mocked_suggestions,
            recipient_email_address=self.fake_recipient_email_address,
        )

        # Then
        assert email_message.subject == DEFAULT_FEEDBACK_EMAIL_SUBJECT

    @mock.patch(f"{MODULE_PATH}.build_body_for_email_v2")
    def test_sets_specified_subject_on_email_message_when_provided(
        self, mocked_build_body_for_email_v2: mock.MagicMock
    ):
        """
        Given a suggestions dict and a recipient email address
        And a specified non-default subject line
        When `create_email_message()` is called
        Then the specified subject line is set on the email message
        """
        # Given
        mocked_suggestions = mock.MagicMock()
        fake_non_default_subject = "Specified example subject"

        # When
        email_message: EmailMessage = create_email_message_v2(
            suggestions=mocked_suggestions,
            recipient_email_address=self.fake_recipient_email_address,
            subject=fake_non_default_subject,
        )

        # Then
        assert email_message.subject == fake_non_default_subject

    @mock.patch(f"{MODULE_PATH}.build_body_for_email_v2")
    def test_sets_specified_recipient_on_email_message_when_provided(
        self, mocked_build_body_for_email_v2: mock.MagicMock
    ):
        """
        Given a suggestions dict and a specified recipient email address
        When `create_email_message()` is called
        Then the specified recipient is set on the recipients of the email message
        """
        # Given
        mocked_suggestions = mock.MagicMock()
        fake_non_default_subject = "Specified example subject"

        # When
        email_message: EmailMessage = create_email_message_v2(
            suggestions=mocked_suggestions,
            recipient_email_address=self.fake_recipient_email_address,
            subject=fake_non_default_subject,
        )

        # Then
        assert self.fake_recipient_email_address in email_message.recipients()


class TestSendEmail:
    @mock.patch(f"{MODULE_PATH}.create_email_message")
    def test_delegates_call_to_create_email_message(
        self, spy_create_email_message: mock.MagicMock
    ):
        """
        Given a suggestions dict, a recipient email address and a subject line
        When `send_email()` is called
        Then the call is delegated to `create_email_message()`

        Patches:
            `spy_create_email_message`: For the main assertion.
                To check the email message object is initialized
                with the correct arguments
        """
        # Given
        mocked_suggestions = mock.Mock()
        mocked_recipient_email_address = mock.Mock()
        mocked_subject = mock.Mock()

        # When
        send_email(
            suggestions=mocked_suggestions,
            recipient_email_address=mocked_recipient_email_address,
            subject=mocked_subject,
        )

        # Then
        spy_create_email_message.assert_called_once_with(
            suggestions=mocked_suggestions,
            subject=mocked_subject,
            recipient_email_address=mocked_recipient_email_address,
        )

    @mock.patch(f"{MODULE_PATH}.create_email_message")
    def test_calls_send_on_email_message(
        self, spy_create_email_message: mock.MagicMock
    ):
        """
        Given a suggestions dict, a recipient email address and a subject line
        When `send_email()` is called
        Then the `send()` is called from the returned `EmailMessage`

        Patches:
            `spy_create_email_message`: To capture and spy on
                the returned `EmailMessage`.
                And to check `send()` is called from the `EmailMessage`
        """
        # Given
        mocked_suggestions = mock.Mock()
        mocked_recipient_email_address = mock.Mock()
        mocked_subject = mock.Mock()
        fail_silently = True

        # When
        send_email(
            suggestions=mocked_suggestions,
            recipient_email_address=mocked_recipient_email_address,
            subject=mocked_subject,
            fail_silently=fail_silently,
        )

        # Then
        email_message = spy_create_email_message.return_value
        email_message.send.assert_called_once_with(fail_silently=fail_silently)


class TestSendEmailV2:
    @mock.patch(f"{MODULE_PATH}.create_email_message_v2")
    def test_delegates_call_to_create_email_message(
        self, spy_create_email_message: mock.MagicMock
    ):
        """
        Given a suggestions dict, a recipient email address and a subject line
        When `send_email()` is called
        Then the call is delegated to `create_email_message()`

        Patches:
            `spy_create_email_message`: For the main assertion.
                To check the email message object is initialized
                with the correct arguments
        """
        # Given
        mocked_suggestions = mock.Mock()
        mocked_recipient_email_address = mock.Mock()
        mocked_subject = mock.Mock()

        # When
        send_email_v2(
            suggestions=mocked_suggestions,
            recipient_email_address=mocked_recipient_email_address,
            subject=mocked_subject,
        )

        # Then
        spy_create_email_message.assert_called_once_with(
            suggestions=mocked_suggestions,
            subject=mocked_subject,
            recipient_email_address=mocked_recipient_email_address,
        )

    @mock.patch(f"{MODULE_PATH}.create_email_message_v2")
    def test_calls_send_on_email_message(
        self, spy_create_email_message: mock.MagicMock
    ):
        """
        Given a suggestions dict, a recipient email address and a subject line
        When `send_email()` is called
        Then the `send()` is called from the returned `EmailMessage`

        Patches:
            `spy_create_email_message`: To capture and spy on
                the returned `EmailMessage`.
                And to check `send()` is called from the `EmailMessage`
        """
        # Given
        mocked_suggestions = mock.Mock()
        mocked_recipient_email_address = mock.Mock()
        mocked_subject = mock.Mock()
        fail_silently = True

        # When
        send_email_v2(
            suggestions=mocked_suggestions,
            recipient_email_address=mocked_recipient_email_address,
            subject=mocked_subject,
            fail_silently=fail_silently,
        )

        # Then
        email_message = spy_create_email_message.return_value
        email_message.send.assert_called_once_with(fail_silently=fail_silently)


class TestSendEmailViaSES:
    @mock.patch(f"{MODULE_PATH}.ses_client")
    def test_send_email_success(
        self,
        mocked_ses_client: mock.MagicMock,
        caplog: LogCaptureFixture,
        monkeypatch: MonkeyPatch,
    ):
        """
        Given a valid `EmailMessage` object
        When `send_email_via_ses()` is called
        Then the call is delegated to the SES client
        And the appropriate logs are written
        """
        # Given
        fake_email_recipient_address = "test-recipient@example.com"
        fake_sender = "UKHSA data dashboard feedback <test-sender@example.com>"
        monkeypatch.setenv(
            "FEEDBACK_EMAIL_RECIPIENT_ADDRESS", fake_email_recipient_address
        )
        monkeypatch.setenv("FEEDBACK_EMAIL_SENDER_ADDRESS", "test-sender@example.com")
        mocked_ses_client.send_email.return_value = {"MessageId": "12345"}
        fake_email_message = EmailMessage(subject="Test Subject", body="Test Body")

        # When
        send_email_via_ses(email_message=fake_email_message)

        # Then
        mocked_ses_client.send_email.assert_called_once_with(
            Destination={"ToAddresses": [fake_email_recipient_address]},
            Message={
                "Body": {"Text": {"Charset": "UTF-8", "Data": fake_email_message.body}},
                "Subject": {"Charset": "UTF-8", "Data": fake_email_message.subject},
            },
            Source=fake_sender,
        )
        assert "Sending email" in caplog.text
        assert "Email sent. Message ID: 12345" in caplog.text

    @mock.patch(f"{MODULE_PATH}.ses_client")
    def test_send_email_client_error(
        self, mocked_ses_client: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given an `EmailMessage` object
        And the SES client which raises a `ClientError`
        When `send_email_via_ses()` is called
        Then the error is logged, and the exception is re-raised
        """
        # Given
        error_message = "An error occurred"
        mocked_ses_client.send_email.side_effect = ClientError(
            {"Error": {"Message": error_message}}, "SendEmail"
        )

        # When
        with pytest.raises(ClientError):
            send_email_via_ses(email_message=mock.Mock())

        # Then
        assert "Sending email" in caplog.text
        assert error_message in caplog.text
