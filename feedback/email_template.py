from django.db.models import Manager

from feedback.cms_interface import CMSInterface

FALLBACK_DID_YOU_FIND_EVERYTHING_ANSWER: str = "User provided no input"
DEFAULT_FORM_PAGE_MANAGER = CMSInterface().get_form_page_manager()


def build_body_for_email_v2(*, suggestions: dict[str, str]) -> str:
    """Builds the suggestions email body as a string to be sent to the email server

    Args:
        suggestions: A dict containing:
            keys - Shortform questions
            values - Answers provided by the user

    Returns:
        A continuous string which represents
        the body of the feedback email

    """
    enriched_suggestions: dict[str, str] = (
        _enrich_suggestions_with_long_form_questions_v2(suggestions=suggestions)
    )
    return _build_body_from_suggestions(suggestions=enriched_suggestions)


def _enrich_suggestions_with_long_form_questions_v2(
    *,
    suggestions: dict[str, str],
    form_page_manager: Manager = DEFAULT_FORM_PAGE_MANAGER,
) -> dict[str, str]:
    """Enriches the question keys in the given `suggestions` with the long form versions

    Examples:
        `suggestions` is provided with the following key value pair:
            `"reason": "some answer"`
            Then the return key value pair would be:
            `"What was your reason for visiting the dashboard today?": "some answer"`

    Args:
        suggestions: Dict of feedback suggestions from the user

    Returns:
        A dict of feedback suggestions with longform questions as the keys
        and answers for the values.

    """
    form_fields = form_page_manager.get_feedback_page_form_fields()

    return {field.label: suggestions.get(field.clean_name) for field in form_fields}


def _build_body_from_suggestions(*, suggestions: dict[str, str]) -> str:
    """Builds the suggestions email body as a string to be sent to the email server

    Args:
        suggestions: A dict containing:
            keys - Longform questions
            values - Answers provided by the user

    Returns:
        A continuous string which represents
        the body of the feedback email

    """
    email_body = ""
    for question, answer in suggestions.items():
        email_body += f"Question: {question}\nAnswer: {answer}\n\n"
    return email_body
