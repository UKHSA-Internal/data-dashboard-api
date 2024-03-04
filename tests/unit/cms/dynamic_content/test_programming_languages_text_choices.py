from cms.dynamic_content.blocks import ProgrammingLanguages


class TestProgrammingLanguagesTextChoices:

    def test_returns_tuple_of_languages(self):
        """
        Given a tuple of expected languages taken from `ProgrammingLanguages` attributes
        When `get_programming_languages()` is called
        Then the expected languages are returned
        """
        # Given
        expected_languages = tuple(
            (item.value, item.value) for item in ProgrammingLanguages
        )

        # When
        returned_languages = ProgrammingLanguages.get_programming_languages()

        # Then
        assert returned_languages == expected_languages
