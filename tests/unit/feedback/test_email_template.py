import pytest

from feedback.email_template import (
    FeedbackQuestion,
    enrich_suggestions_with_long_form_questions,
)


class TestEnrichSuggestionsWithLongFormQuestions:
    @staticmethod
    def _build_base_suggestions() -> dict[str, str]:
        return {
            FeedbackQuestion.reason.name: "N/A",
            FeedbackQuestion.improve_experience.name: "N/A",
            FeedbackQuestion.like_to_see.name: "N/A",
            FeedbackQuestion.did_you_find_everything.name: "no",
        }

    @pytest.mark.parametrize(
        "question, answer",
        (
            [
                FeedbackQuestion.reason,
                "I wanted to understand infection rates of Disease X in my local area",
            ],
            [
                FeedbackQuestion.improve_experience,
                "More contextual information about data sources would be useful",
            ],
            [
                FeedbackQuestion.like_to_see,
                "It would be good to see more localised/regional data on the dashboard",
            ],
            [FeedbackQuestion.did_you_find_everything, "no"],
        ),
    )
    def test_returns_correct_dict(self, question: FeedbackQuestion, answer: str):
        """
        Given a `suggestions` dict
        When `enrich_suggestions_with_long_form_questions()` is called
        Then a dict is returned with longform questions as the keys
        """
        # Given
        suggestions = self._build_base_suggestions()
        suggestions[question.name] = answer

        # When
        enriched_suggestions: dict[
            str, str
        ] = enrich_suggestions_with_long_form_questions(suggestions=suggestions)

        # Then
        assert enriched_suggestions[question.value] == answer
