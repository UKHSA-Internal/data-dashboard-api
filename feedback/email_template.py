from enum import Enum

FALLBACK_DID_YOU_FIND_EVERYTHING_ANSWER: str = "User provided no input"


def build_body_for_email(*, suggestions: dict[str, str]) -> str:
    """Builds the suggestions email body as a string to be sent to the email server

    Args:
        suggestions: A dict containing:
            keys - Shortform questions
            values - Answers provided by the user

    Returns:
        A continuous string which represents
        the body of the feedback email

    """
    enriched_suggestions: dict[str, str] = _enrich_suggestions_with_long_form_questions(
        suggestions=suggestions
    )
    return _build_body_from_suggestions(suggestions=enriched_suggestions)


class FeedbackQuestion(Enum):
    reason = "What was your reason for visiting the dashboard today?"
    did_you_find_everything = "Did you find everything you were looking for?"
    improve_experience = "How could we improve your experience with the dashboard?"
    like_to_see = "What would you like to see on the dashboard in the future?"

    @classmethod
    def string_based_questions(cls) -> list["FeedbackQuestion"]:
        return [cls.reason, cls.improve_experience, cls.like_to_see]


def _enrich_suggestions_with_long_form_questions(
    *, suggestions: dict[str, str]
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
    long_form_suggestions = {
        question.value: suggestions[question.name]
        for question in FeedbackQuestion.string_based_questions()
    }

    did_you_find_everything_enum: FeedbackQuestion = (
        FeedbackQuestion.did_you_find_everything
    )
    # Use the `did_you_find_everything` field from the `suggestions` input
    # If not available, use the fallback
    did_you_find_everything_answer = (
        suggestions.get(did_you_find_everything_enum.name, "")
        or FALLBACK_DID_YOU_FIND_EVERYTHING_ANSWER
    )
    long_form_suggestions[did_you_find_everything_enum.value] = (
        did_you_find_everything_answer
    )

    return long_form_suggestions


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
