import logging

from django.core.mail import EmailMessage

import config
from feedback.email_template import build_body_for_email

logger = logging.getLogger(__name__)

DEFAULT_FEEDBACK_EMAIL_RECIPIENT_ADDRESS = config.FEEDBACK_EMAIL_RECIPIENT_ADDRESS
DEFAULT_FEEDBACK_EMAIL_SUBJECT = "Suggestions Feedback for UKHSA data dashboard"


def send_email(
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

    email_was_sent = bool(email.send(fail_silently=fail_silently))

    return email_was_sent


def create_email_message(
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
