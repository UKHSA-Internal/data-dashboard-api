from enum import Enum


def build_body_for_email(suggestions: dict[str, str]) -> str:
    """Builds the suggestions email body as a string to be sent to the email server

    Args:
        suggestions: A dict containing:
            keys - Shortform questions
            values - Answers provided by the user

    Returns:
        A continuous string which represents
        the body of the feedback email

    """
    enriched_suggestions = _enrich_suggestions_with_long_form_questions(
        suggestions=suggestions
    )
    return _build_body_from_suggestions(suggestions=enriched_suggestions)


class FeedbackQuestion(Enum):
    reason = "What was your reason for visiting the dashboard today?"
    improve_experience = "How could we improve your experience with the dashboard?"
    like_to_see = "What would you like to see on the dashboard in the future?"
    did_you_find_everything = "Did you find everything you were looking for?"


def _enrich_suggestions_with_long_form_questions(
    suggestions: dict[str, str]
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
    return {
        question.value: suggestions[question.name]
        for question in list(FeedbackQuestion)
    }


def _build_body_from_suggestions(suggestions: dict[str, str]) -> str:
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
