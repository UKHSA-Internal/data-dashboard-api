from unittest import mock

import pytest

from cms.forms.models import FormField
from feedback.email_template import (
    FALLBACK_DID_YOU_FIND_EVERYTHING_ANSWER,
    FeedbackQuestion,
    _build_body_from_suggestions,
    _enrich_suggestions_with_long_form_questions,
    build_body_for_email,
    build_body_for_email_v2,
    _enrich_suggestions_with_long_form_questions_v2,
)

REASON_ANSWER = "I wanted to understand infection rates of Disease X in my local area"
IMPROVE_EXPERIENCE_ANSWER = (
    "More contextual information about data sources would be useful"
)
LIKE_TO_SEE_ANSWER = (
    "It would be good to see more localised/regional data on the dashboard"
)
DID_YOU_FIND_EVERYTHING_ANSWER = "No"


MODULE_PATH = "feedback.email_template"


@pytest.fixture
def example_feedback_form_fields() -> list[FormField]:
    return [
        FormField(
            clean_name="how_could_we_improve_your_experience_with_the_dashboard",
            label="How could we improve your experience with the dashboard?",
            field_type="multiline",
            required=False,
        ),
        FormField(
            clean_name="what_would_you_like_to_see_on_the_dashboard_in_the_future",
            label="What would you like to see on the dashboard in the future?",
            field_type="multiline",
            required=False,
        ),
        FormField(
            clean_name="did_you_find_everything_you_were_looking_for",
            label="Did you find everything you were looking for?",
            field_type="radio",
            required=False,
            choices="Yes\r\nNo",
        ),
        FormField(
            clean_name="what_was_your_reason_for_visiting_the_dashboard_today",
            label="What was your reason for visiting the dashboard today?",
            field_type="multiline",
            required=False,
        ),
    ]


class TestFeedbackQuestion:
    def test_string_based_questions(self):
        """
        Given no input
        When the `string_based_questions()` class method
            is called from the `FeedbackQuestion` class
        Then the correct `FeedbackQuestion` enums are returned
        """
        # Given / When
        string_based_questions = FeedbackQuestion.string_based_questions()

        # Then
        assert FeedbackQuestion.reason in string_based_questions
        assert FeedbackQuestion.improve_experience in string_based_questions
        assert FeedbackQuestion.like_to_see in string_based_questions

        assert FeedbackQuestion.did_you_find_everything not in string_based_questions


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
                REASON_ANSWER,
            ],
            [
                FeedbackQuestion.improve_experience,
                IMPROVE_EXPERIENCE_ANSWER,
            ],
            [
                FeedbackQuestion.like_to_see,
                LIKE_TO_SEE_ANSWER,
            ],
            [FeedbackQuestion.did_you_find_everything, DID_YOU_FIND_EVERYTHING_ANSWER],
        ),
    )
    def test_returns_correct_dict(self, question: FeedbackQuestion, answer: str):
        """
        Given a `suggestions` dict
        When `_enrich_suggestions_with_long_form_questions()` is called
        Then a dict is returned with longform questions as the keys
        """
        # Given
        suggestions = self._build_base_suggestions()
        suggestions[question.name] = answer

        # When
        enriched_suggestions: dict[str, str] = (
            _enrich_suggestions_with_long_form_questions(suggestions=suggestions)
        )

        # Then
        assert enriched_suggestions[question.value] == answer

    def test_uses_default_value_when_did_you_find_everything_field_not_provided(self):
        """
        Given a dict which does not contain a value for the *did_you_find_everything* key
        When `_enrich_suggestions_with_long_form_questions()` is called
        Then a dict is returned with longform questions as the keys
        And a fallback values is included for the *did_you_find_everything* key
        """
        # Given
        suggestions = self._build_base_suggestions()
        suggestions.pop("did_you_find_everything")

        # When
        enriched_suggestions: dict[str, str] = (
            _enrich_suggestions_with_long_form_questions(suggestions=suggestions)
        )

        # Then
        for question in FeedbackQuestion.string_based_questions():
            assert enriched_suggestions[question.value] == suggestions[question.name]

        assert (
            enriched_suggestions[FeedbackQuestion.did_you_find_everything.value]
            == FALLBACK_DID_YOU_FIND_EVERYTHING_ANSWER
        )

    @pytest.mark.parametrize("did_you_find_everything_value", ["", None])
    def test_uses_default_value_when_did_you_find_everything_field_provided_as_falsy_value(
        self, did_you_find_everything_value: str | None
    ):
        """
        Given a dict which does not contain a value for the *did_you_find_everything* key
        When `_enrich_suggestions_with_long_form_questions()` is called
        Then a dict is returned with longform questions as the keys
        And a fallback values is included for the *did_you_find_everything* key
        """
        # Given
        suggestions = self._build_base_suggestions()
        suggestions[FeedbackQuestion.did_you_find_everything.name] = (
            did_you_find_everything_value
        )

        # When
        enriched_suggestions: dict[str, str] = (
            _enrich_suggestions_with_long_form_questions(suggestions=suggestions)
        )

        # Then
        for question in FeedbackQuestion.string_based_questions():
            assert enriched_suggestions[question.value] == suggestions[question.name]

        assert (
            enriched_suggestions[FeedbackQuestion.did_you_find_everything.value]
            == FALLBACK_DID_YOU_FIND_EVERYTHING_ANSWER
        )


class TestEnrichSuggestionsWithLongFormQuestionsV2:
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
                REASON_ANSWER,
            ],
            [
                FeedbackQuestion.improve_experience,
                IMPROVE_EXPERIENCE_ANSWER,
            ],
            [
                FeedbackQuestion.like_to_see,
                LIKE_TO_SEE_ANSWER,
            ],
            [FeedbackQuestion.did_you_find_everything, DID_YOU_FIND_EVERYTHING_ANSWER],
        ),
    )
    def test_returns_correct_dict(
        self,
        question: FeedbackQuestion,
        answer: str,
        example_feedback_form_fields: list[FormField],
    ):
        """
        Given a `suggestions` dict
        When `_enrich_suggestions_with_long_form_questions()` is called
        Then a dict is returned with longform questions as the keys
        """
        # Given
        suggestions = {
            "how_could_we_improve_your_experience_with_the_dashboard": IMPROVE_EXPERIENCE_ANSWER,
            "what_would_you_like_to_see_on_the_dashboard_in_the_future": LIKE_TO_SEE_ANSWER,
            "did_you_find_everything_you_were_looking_for": DID_YOU_FIND_EVERYTHING_ANSWER,
            "what_was_your_reason_for_visiting_the_dashboard_today": REASON_ANSWER,
        }
        mocked_form_page_manager = mock.Mock()
        mocked_form_page_manager.get_feedback_page_form_fields.return_value = (
            example_feedback_form_fields
        )

        # When
        enriched_suggestions: dict[str, str] = (
            _enrich_suggestions_with_long_form_questions_v2(
                suggestions=suggestions,
                form_page_manager=mocked_form_page_manager,
            )
        )

        # Then
        assert enriched_suggestions[question.value] == answer


class TestBuildBodyFromSuggestions:
    def test_returns_expected_string(self):
        """
        Given an enriched suggestions dict containing question and answers
        When `_build_body_from_suggestions()` is called
        Then a string is returned containing the question and answers
        """
        # Given
        enriched_suggestions = {
            FeedbackQuestion.reason.value: REASON_ANSWER,
            FeedbackQuestion.improve_experience.value: IMPROVE_EXPERIENCE_ANSWER,
            FeedbackQuestion.like_to_see.value: LIKE_TO_SEE_ANSWER,
            FeedbackQuestion.did_you_find_everything.value: DID_YOU_FIND_EVERYTHING_ANSWER,
        }

        # When
        email_body: str = _build_body_from_suggestions(suggestions=enriched_suggestions)

        # Then
        question_answers: list[str] = [
            f"Question: {question}\nAnswer: {answer}\n\n"
            for question, answer in enriched_suggestions.items()
        ]
        expected_email_body = "".join(question_answers)
        assert email_body == expected_email_body


class TestBuildBodyForEmail:
    def test_returns_correct_string(self):
        """
        Given a suggestions dict containing question and answers
        When `build_body_for_email()` is called
        Then a string is returned containing the question and answers
        """
        # Given
        suggestions = {
            FeedbackQuestion.reason.name: REASON_ANSWER,
            FeedbackQuestion.improve_experience.name: IMPROVE_EXPERIENCE_ANSWER,
            FeedbackQuestion.like_to_see.name: LIKE_TO_SEE_ANSWER,
            FeedbackQuestion.did_you_find_everything.name: DID_YOU_FIND_EVERYTHING_ANSWER,
        }

        # When
        email_body: str = build_body_for_email(suggestions=suggestions)

        # Then
        question_answers: list[str] = [
            f"Question: {FeedbackQuestion[question].value}\nAnswer: {answer}\n\n"
            for question, answer in suggestions.items()
        ]
        expected_email_body = "".join(question_answers)
        assert email_body == expected_email_body

    @mock.patch(f"{MODULE_PATH}._build_body_from_suggestions")
    @mock.patch(f"{MODULE_PATH}._enrich_suggestions_with_long_form_questions")
    def test_delegates_calls_correctly(
        self,
        spy_enrich_suggestions_with_long_form_questions: mock.MagicMock,
        spy_build_body_from_suggestions: mock.MagicMock,
    ):
        """
        Given a suggestions dict containing question and answers
        When `build_body_for_email()` is called
        Then the call is delegated accordingly

        Patches:
            `spy_enrich_suggestions_with_long_form_questions`: To check
                the initial input suggestions dict is parsed and
                enriched with the longform question first
            `spy_build_body_from_suggestions`: To check the
                call is delegated to the correct callee function
                with the return value from the previous call
        """
        # Given
        mocked_suggestions = mock.Mock()

        # When
        build_body_for_email(suggestions=mocked_suggestions)

        # Then
        spy_enrich_suggestions_with_long_form_questions.assert_called_once_with(
            suggestions=mocked_suggestions
        )
        spy_build_body_from_suggestions.assert_called_once_with(
            suggestions=spy_enrich_suggestions_with_long_form_questions.return_value
        )


class TestBuildBodyForEmailV2:
    @mock.patch(f"{MODULE_PATH}._enrich_suggestions_with_long_form_questions_v2")
    def test_returns_correct_string(
        self, spy_enrich_suggestions_with_long_form_questions_v2: mock.MagicMock
    ):
        """
        Given a suggestions dict containing question and answers
        When `build_body_for_email()` is called
        Then a string is returned containing the question and answers
        """
        # Given
        mocked_suggestions = mock.Mock()
        enriched_suggestions = {
            "How could we improve your experience with the dashboard?": IMPROVE_EXPERIENCE_ANSWER,
            "What would you like to see on the dashboard in the future?": LIKE_TO_SEE_ANSWER,
            "Did you find everything you were looking for?": DID_YOU_FIND_EVERYTHING_ANSWER,
            "What was your reason for visiting the dashboard today?": REASON_ANSWER,
        }
        spy_enrich_suggestions_with_long_form_questions_v2.return_value = (
            enriched_suggestions
        )

        # When
        email_body: str = build_body_for_email_v2(suggestions=mocked_suggestions)

        # Then
        spy_enrich_suggestions_with_long_form_questions_v2.assert_called_once_with(
            suggestions=mocked_suggestions
        )
        expected_email_body = _build_body_from_suggestions(
            suggestions=enriched_suggestions
        )
        assert email_body == expected_email_body

    @mock.patch(f"{MODULE_PATH}._build_body_from_suggestions")
    @mock.patch(f"{MODULE_PATH}._enrich_suggestions_with_long_form_questions_v2")
    def test_delegates_calls_correctly(
        self,
        spy_enrich_suggestions_with_long_form_questions: mock.MagicMock,
        spy_build_body_from_suggestions: mock.MagicMock,
    ):
        """
        Given a suggestions dict containing question and answers
        When `build_body_for_email()` is called
        Then the call is delegated accordingly

        Patches:
            `spy_enrich_suggestions_with_long_form_questions`: To check
                the initial input suggestions dict is parsed and
                enriched with the longform question first
            `spy_build_body_from_suggestions`: To check the
                call is delegated to the correct callee function
                with the return value from the previous call
        """
        # Given
        mocked_suggestions = mock.Mock()

        # When
        build_body_for_email_v2(suggestions=mocked_suggestions)

        # Then
        spy_enrich_suggestions_with_long_form_questions.assert_called_once_with(
            suggestions=mocked_suggestions
        )
        spy_build_body_from_suggestions.assert_called_once_with(
            suggestions=spy_enrich_suggestions_with_long_form_questions.return_value
        )
