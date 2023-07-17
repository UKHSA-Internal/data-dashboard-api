import logging

from django.core.mail import EmailMessage

from feedback.email_template import build_body_for_email

logger = logging.getLogger(__name__)


def send_email(suggestions: dict[str, str]) -> None:
    body = build_body_for_email(suggestions)

    EmailMessage(
        subject="Suggestions Feedback for UKHSA data dashboard",
        body=body,
        to=["afaan.ashiq2@gmail.com"],
    )
