from enum import Enum


class FeedbackQuestion(Enum):
    reason = "What was your reason for visiting the dashboard today?"
    improve_experience = "How could we improve your experience with the dashboard?"
    like_to_see = "What would you like to see on the dashboard in the future?"
    did_you_find_everything = "Did you find everything you were looking for?"


def enrich_suggestions_with_long_form_questions(
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
