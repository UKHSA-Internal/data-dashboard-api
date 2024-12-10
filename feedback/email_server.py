import contextlib
import logging
import os

import boto3
from botocore.exceptions import ClientError
from django.core.mail import EmailMessage

import config
from feedback.email_template import build_body_for_email, build_body_for_email_v2

logger = logging.getLogger(__name__)

DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS = config.FEEDBACK_EMAIL_RECIPIENT_ADDRESS
DEFAULT_FEEDBACK_EMAIL_SUBJECT = "Suggestions Feedback for UKHSA data dashboard"

ses_client = boto3.client("ses", region_name="eu-west-2")


def send_email_via_ses(*, email_message: EmailMessage) -> None:
    """Sends the given `email_message` via AWS SES

    Notes:
        Sends the email from the env var `FEEDBACK_EMAIL_SENDER_ADDRESS`
        to the recipient address from the env var `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`

    Returns:
        None

    Raises:
        `ClientError`: If there is an error sending the email via AWS SES

    """
    feedback_email_recipient_address = os.environ.get(
        "FEEDBACK_EMAIL_RECIPIENT_ADDRESS"
    )
    feedback_email_sender_address = os.environ.get("FEEDBACK_EMAIL_SENDER_ADDRESS")
    sender = f"UKHSA data dashboard feedback <{feedback_email_sender_address}>"

    logger.info("Sending email")
    charset = "UTF-8"
    try:
        response = ses_client.send_email(
            Destination={"ToAddresses": [feedback_email_recipient_address]},
            Message={
                "Body": {"Text": {"Charset": charset, "Data": email_message.body}},
                "Subject": {"Charset": charset, "Data": email_message.subject},
            },
            Source=sender,
        )
    except ClientError as error:
        logger.info(error.response["Error"]["Message"])
        raise
    else:
        logger.info("Email sent. Message ID: %s", response["MessageId"]),


def send_email(
    *,
    suggestions: dict[str, str],
    subject: str = DEFAULT_FEEDBACK_EMAIL_SUBJECT,
    recipient_email_address: str = DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS,
    fail_silently: bool = True,
) -> bool:
    """Sends a feedback email to the `recipient_email_address`

    Args:
        suggestions: Dict of feedback suggestions from the user
            E.g. {"question": "some question", "answer": "some answer"}
        subject: The subject line to set on the email message
            Defaults to "Suggestions Feedback for UKHSA data dashboard"
        recipient_email_address: The recipient to send the email to
            Defaults to the environment variable
                `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`
        fail_silently: Switch to raise an exception
            if the email failed and was not successfully sent.
            Defaults to True

    Returns:
        A boolean to describe whether the email has been sent successfully

    """
    email = create_email_message(
        suggestions=suggestions,
        subject=subject,
        recipient_email_address=recipient_email_address,
    )

    return bool(email.send(fail_silently=fail_silently))


def send_email_v2(
    *,
    suggestions: dict[str, str],
    subject: str = DEFAULT_FEEDBACK_EMAIL_SUBJECT,
    recipient_email_address: str = DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS,
    fail_silently: bool = True,
) -> None:
    """Sends a feedback email to the `recipient_email_address`

    Args:
        suggestions: Dict of feedback suggestions from the user
            E.g. {"question": "some question", "answer": "some answer"}
        subject: The subject line to set on the email message
            Defaults to "Suggestions Feedback for UKHSA data dashboard"
        recipient_email_address: The recipient to send the email to
            Defaults to the environment variable
                `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`
        fail_silently: Switch to raise an exception
            if the email failed and was not successfully sent.
            Defaults to True

    Returns:
        None

    """
    email = create_email_message_v2(
        suggestions=suggestions,
        subject=subject,
        recipient_email_address=recipient_email_address,
    )

    email_submitted = bool(email.send(fail_silently=fail_silently))
    message = "succeeded" if email_submitted else "failed"
    logger.info("Email submission %s for %s", message, subject)


def send_email_v3(
    *,
    suggestions: dict[str, str],
    subject: str = DEFAULT_FEEDBACK_EMAIL_SUBJECT,
    recipient_email_address: str = DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS,
) -> None:
    """Sends a feedback email to the `recipient_email_address` via AWS SES

    Args:
        suggestions: Dict of feedback suggestions from the user
            E.g. {"question": "some question", "answer": "some answer"}
        subject: The subject line to set on the email message
            Defaults to "Suggestions Feedback for UKHSA data dashboard"
        recipient_email_address: The recipient to send the email to
            Defaults to the environment variable
                `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`

    Returns:
        None

    """
    email_message: EmailMessage = create_email_message_v2(
        suggestions=suggestions,
        subject=subject,
        recipient_email_address=recipient_email_address,
    )
    with contextlib.suppress(ClientError):
        send_email_via_ses(email_message=email_message)


def create_email_message(
    *,
    suggestions: dict[str, str],
    subject: str = DEFAULT_FEEDBACK_EMAIL_SUBJECT,
    recipient_email_address: str = DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS,
) -> EmailMessage:
    """Creates an `EmailMessage` object for a feedback email

    Notes:
        This returns an `EmailMessage` object which **has not been sent**

    Args:
        suggestions: Dict of feedback suggestions from the user
            E.g. {"question": "some question", "answer": "some answer"}
        subject: The subject line to set on the email message
            Defaults to "Suggestions Feedback for UKHSA data dashboard"
        recipient_email_address: The recipient to send the email to
            Defaults to the environment variable
                `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`
    Returns:
        An `EmailMessage` object with the subject, body and recipient
        set on the object

    """
    body: str = build_body_for_email(suggestions=suggestions)

    return EmailMessage(
        subject=subject,
        body=body,
        to=[recipient_email_address],
    )


def create_email_message_v2(
    *,
    suggestions: dict[str, str],
    subject: str = DEFAULT_FEEDBACK_EMAIL_SUBJECT,
    recipient_email_address: str = DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS,
) -> EmailMessage:
    """Creates an `EmailMessage` object for a feedback email

    Notes:
        This returns an `EmailMessage` object which **has not been sent**

    Args:
        suggestions: Dict of feedback suggestions from the user
            E.g. {"question": "some question", "answer": "some answer"}
        subject: The subject line to set on the email message
            Defaults to "Suggestions Feedback for UKHSA data dashboard"
        recipient_email_address: The recipient to send the email to
            Defaults to the environment variable
                `FEEDBACK_EMAIL_RECIPIENT_ADDRESS`
    Returns:
        An `EmailMessage` object with the subject, body and recipient
        set on the object

    """
    body: str = build_body_for_email_v2(suggestions=suggestions)

    return EmailMessage(
        subject=subject,
        body=body,
        to=[recipient_email_address],
    )
