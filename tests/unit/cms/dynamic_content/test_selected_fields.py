from unittest import mock

import pytest

from cms.dynamic_content.selected_fields import CMSSelectedFieldParser

MODULE_PATH = "cms.dynamic_content.selected_fields"


@pytest.fixture(autouse=True)
def mock_dual_category_check():
    """Treat any block carrying `static_fields` as a dual-category chart block."""
    with mock.patch(
        f"{MODULE_PATH}.is_dual_category_chart_block",
        side_effect=lambda block: "static_fields" in block,
    ):
        yield


def _plot(topic: str, theme: str | None = None, sub_theme: str | None = None) -> dict:
    value: dict[str, any] = {"topic": topic, "metric": f"{topic}_metric"}
    if theme is not None:
        value["theme"] = theme
    if sub_theme is not None:
        value["sub_theme"] = sub_theme
    return {"value": value}


class TestCMSSelectedFieldParser:
    @staticmethod
    def _build_standard_block(*plot_values: dict) -> dict:
        return {"chart": [{"value": value} for value in plot_values]}

    @mock.patch(f"{MODULE_PATH}.is_dual_category_chart_block", return_value=False)
    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_collects_unique_values_from_standard_chart_blocks(
        self, spy_cms_block_parser: mock.MagicMock, mock_is_dual: mock.MagicMock
    ):
        """
        Given chart blocks whose plots select themes and sub themes
        When the `*_from_sections()` methods are called
        Then the unique values are returned as sets of strings
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = [
            self._build_standard_block(
                {"theme": "infectious_disease", "sub_theme": "respiratory"},
                {"theme": "infectious_disease", "sub_theme": "respiratory"},
            ),
            self._build_standard_block(
                {"theme": "extreme_event", "sub_theme": "weather_alert"},
            ),
        ]

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )
        sub_themes = CMSSelectedFieldParser.get_all_selected_sub_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == {"infectious_disease", "extreme_event"}
        assert sub_themes == {"respiratory", "weather_alert"}

    @mock.patch(f"{MODULE_PATH}.is_dual_category_chart_block", return_value=True)
    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_reads_static_fields_for_dual_category_chart_blocks(
        self, spy_cms_block_parser: mock.MagicMock, mock_is_dual: mock.MagicMock
    ):
        """
        Given a dual category chart block
        When `get_all_selected_theme_from_sections()` is called
        Then the theme is read from the block's `static_fields`
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = [
            {
                "static_fields": {
                    "theme": "infectious_disease",
                    "sub_theme": "respiratory",
                }
            }
        ]

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == {"infectious_disease"}

    @pytest.mark.parametrize("empty_value", [None, ""])
    @mock.patch(f"{MODULE_PATH}.is_dual_category_chart_block", return_value=False)
    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_skips_missing_or_empty_values(
        self,
        spy_cms_block_parser: mock.MagicMock,
        mock_is_dual: mock.MagicMock,
        empty_value,
    ):
        """
        Given plots with a missing, None or empty theme
        When `get_all_selected_theme_from_sections()` is called
        Then those plots are skipped
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = [
            self._build_standard_block(
                {"theme": empty_value},
                {},
                {"theme": "infectious_disease"},
            )
        ]

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == {"infectious_disease"}

    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_returns_empty_set_when_there_are_no_chart_blocks(
        self, spy_cms_block_parser: mock.MagicMock
    ):
        """
        Given sections which contain no chart blocks
        When `get_all_selected_theme_from_sections()` is called
        Then an empty set is returned
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = []

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == set()


@pytest.fixture(autouse=True)
def mock_dual_category_check():
    """Treat any block carrying `static_fields` as a dual-category chart block."""
    with mock.patch(
        "cms.dynamic_content.selected_fields.is_dual_category_chart_block",
        side_effect=lambda block: "static_fields" in block,
    ):
        yield


def _plot(topic: str, theme: str | None = None, sub_theme: str | None = None) -> dict:
    value: dict[str, any] = {"topic": topic, "metric": f"{topic}_metric"}
    if theme is not None:
        value["theme"] = theme
    if sub_theme is not None:
        value["sub_theme"] = sub_theme
    return {"value": value}


def _chart_block(plots: list[dict], headline_number_columns: list[dict] | None = None):
    block: dict[str, any] = {"chart": plots}
    if headline_number_columns:
        block["headline_number_columns"] = headline_number_columns
    return block


def _dual_category_chart_block(
    topic: str, theme: str | None = None, sub_theme: str | None = None
) -> dict:
    static_fields: dict[str, any] = {"topic": topic, "metric": f"{topic}_metric"}
    if theme is not None:
        static_fields["theme"] = theme
    if sub_theme is not None:
        static_fields["sub_theme"] = sub_theme
    return {"static_fields": static_fields, "chart": []}


def _headline_block(
    topic: str, theme: str | None = None, sub_theme: str | None = None
) -> dict:
    return _plot(topic=topic, theme=theme, sub_theme=sub_theme)


def _chart_row_card(chart_blocks: list[dict]) -> dict:
    return {
        "type": "chart_row_card",
        "value": {"columns": [{"value": block} for block in chart_blocks]},
    }


def _headline_row_card(headline_blocks: list[dict]) -> dict:
    return {
        "type": "headline_numbers_row_card",
        "value": {"columns": [{"value": {"rows": headline_blocks}}]},
    }


def _section(*content_cards: dict) -> dict:
    return {"value": {"content": list(content_cards)}}


class TestGetAllSelectedCombinationsFromSections:
    def test_returns_empty_set_for_no_sections(self):
        """
        Given no sections
        When `get_all_selected_combinations_from_sections()` is called
        Then an empty set is returned
        """
        # Given / When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=[]
            )
        )

        # Then
        assert combinations == set()

    def test_extracts_combination_from_chart_plot(self):
        """
        Given a section with a single plot carrying a topic, theme and sub-theme
        When `get_all_selected_combinations_from_sections()` is called
        Then the three values are returned together as one tuple
        """
        # Given
        sections = [
            _section(
                _chart_row_card(
                    [
                        _chart_block(
                            [_plot("COVID-19", "infectious_disease", "respiratory")]
                        )
                    ]
                )
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "infectious_disease", "respiratory")}

    def test_keeps_values_from_each_plot_together(self):
        """
        Given a chart whose plots belong to different topics
        When `get_all_selected_combinations_from_sections()` is called
        Then each theme and sub-theme stays paired with its own topic
        """
        # Given
        sections = [
            _section(
                _chart_row_card(
                    [
                        _chart_block(
                            [
                                _plot("COVID-19", "infectious_disease", "respiratory"),
                                _plot("ticks", "climate_and_environment", "vectors"),
                            ]
                        )
                    ]
                )
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {
            ("COVID-19", "infectious_disease", "respiratory"),
            ("ticks", "climate_and_environment", "vectors"),
        }

    def test_extracts_combination_from_dual_category_chart_block(self):
        """
        Given a dual-category chart block
        When `get_all_selected_combinations_from_sections()` is called
        Then the combination is read from the `static_fields`
        """
        # Given
        sections = [
            _section(
                _chart_row_card(
                    [
                        _dual_category_chart_block(
                            "COVID-19", "infectious_disease", "respiratory"
                        )
                    ]
                )
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "infectious_disease", "respiratory")}

    def test_identical_combinations_are_deduplicated(self):
        """
        Given several plots which share the same topic, theme and sub-theme
            but use different metrics
        When `get_all_selected_combinations_from_sections()` is called
        Then only one tuple is returned
        """
        # Given
        sections = [
            _section(
                _chart_row_card(
                    [
                        _chart_block(
                            [
                                _plot("COVID-19", "infectious_disease", "respiratory"),
                                _plot("COVID-19", "infectious_disease", "respiratory"),
                            ]
                        ),
                        _chart_block(
                            [_plot("COVID-19", "infectious_disease", "respiratory")]
                        ),
                    ]
                )
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "infectious_disease", "respiratory")}

    def test_combinations_are_collected_across_sections(self):
        """
        Given two sections each containing a chart
        When `get_all_selected_combinations_from_sections()` is called
        Then the combinations from both sections are returned
        """
        # Given
        sections = [
            _section(
                _chart_row_card(
                    [
                        _chart_block(
                            [_plot("COVID-19", "infectious_disease", "respiratory")]
                        )
                    ]
                )
            ),
            _section(
                _chart_row_card(
                    [
                        _chart_block(
                            [_plot("ticks", "climate_and_environment", "vectors")]
                        )
                    ]
                )
            ),
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {
            ("COVID-19", "infectious_disease", "respiratory"),
            ("ticks", "climate_and_environment", "vectors"),
        }

    def test_missing_theme_and_sub_theme_become_empty_strings(self):
        """
        Given a plot with no theme or sub-theme
        When `get_all_selected_combinations_from_sections()` is called
        Then empty strings are used, so the tuples remain sortable
        """
        # Given
        sections = [_section(_chart_row_card([_chart_block([_plot("COVID-19")])]))]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "", "")}
        sorted(combinations)  # must not raise

    def test_none_theme_values_become_empty_strings(self):
        """
        Given a plot whose theme and sub-theme are explicitly `None`
        When `get_all_selected_combinations_from_sections()` is called
        Then empty strings are used instead of `None`
        """
        # Given
        plot = {
            "value": {
                "topic": "COVID-19",
                "metric": "m",
                "theme": None,
                "sub_theme": None,
            }
        }
        sections = [_section(_chart_row_card([_chart_block([plot])]))]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "", "")}


class TestHeadlineBlocksInCombinations:
    def test_headline_only_topic_is_kept(self):
        """
        Given a topic which only appears in a headline number block
        When `get_all_selected_combinations_from_sections()` is called
        Then the topic is not lost from the combinations
        """
        # Given
        sections = [_section(_headline_row_card([_headline_block("ticks")]))]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("ticks", "", "")}

    def test_headline_block_inside_chart_card_is_included(self):
        """
        Given a headline block nested inside a chart card
        When `get_all_selected_combinations_from_sections()` is called
        Then its topic is included
        """
        # Given
        sections = [
            _section(
                _chart_row_card(
                    [
                        _chart_block(
                            plots=[
                                _plot("COVID-19", "infectious_disease", "respiratory")
                            ],
                            headline_number_columns=[_headline_block("ticks")],
                        )
                    ]
                )
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {
            ("COVID-19", "infectious_disease", "respiratory"),
            ("ticks", "", ""),
        }

    def test_incomplete_headline_combination_is_dropped_when_topic_has_complete_one(
        self,
    ):
        """
        Given a headline block with no theme for a topic
        And a chart plot with a complete combination for the same topic
        When `get_all_selected_combinations_from_sections()` is called
        Then only the complete combination remains
        """
        # Given
        sections = [
            _section(
                _headline_row_card([_headline_block("COVID-19")]),
                _chart_row_card(
                    [
                        _chart_block(
                            [_plot("COVID-19", "infectious_disease", "respiratory")]
                        )
                    ]
                ),
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "infectious_disease", "respiratory")}

    def test_headline_with_complete_combination_is_kept(self):
        """
        Given a headline block which carries a theme and sub-theme
        When `get_all_selected_combinations_from_sections()` is called
        Then its combination is returned
        """
        # Given
        sections = [
            _section(
                _headline_row_card(
                    [_headline_block("COVID-19", "infectious_disease", "respiratory")]
                )
            )
        ]

        # When
        combinations = (
            CMSSelectedFieldParser.get_all_selected_combinations_from_sections(
                sections=sections
            )
        )

        # Then
        assert combinations == {("COVID-19", "infectious_disease", "respiratory")}


class TestDropRedundantIncompleteCombinations:
    def test_keeps_all_complete_combinations(self):
        # Given
        combinations = {
            ("COVID-19", "infectious_disease", "respiratory"),
            ("COVID-19", "infectious_disease", "vaccination"),
        }

        # When
        result = CMSSelectedFieldParser._drop_redundant_incomplete_combinations(
            combinations
        )

        # Then
        assert result == combinations

    def test_keeps_incomplete_combination_when_topic_has_no_complete_one(self):
        # Given
        combinations = {
            ("ticks", "", ""),
            ("COVID-19", "infectious_disease", "respiratory"),
        }

        # When
        result = CMSSelectedFieldParser._drop_redundant_incomplete_combinations(
            combinations
        )

        # Then
        assert result == combinations

    @pytest.mark.parametrize(
        "incomplete_combination",
        [
            ("COVID-19", "", ""),
            ("COVID-19", "infectious_disease", ""),
            ("COVID-19", "", "respiratory"),
        ],
    )
    def test_drops_incomplete_combination_when_topic_has_complete_one(
        self, incomplete_combination: tuple[str, str, str]
    ):
        # Given
        complete = ("COVID-19", "infectious_disease", "respiratory")
        combinations = {complete, incomplete_combination}

        # When
        result = CMSSelectedFieldParser._drop_redundant_incomplete_combinations(
            combinations
        )

        # Then
        assert result == {complete}

    def test_only_drops_incomplete_combinations_for_the_matching_topic(self):
        # Given
        combinations = {
            ("COVID-19", "infectious_disease", "respiratory"),
            ("ticks", "", ""),
        }

        # When
        result = CMSSelectedFieldParser._drop_redundant_incomplete_combinations(
            combinations
        )

        # Then
        assert ("ticks", "", "") in result

    def test_returns_empty_set_for_empty_input(self):
        # Given / When
        result = CMSSelectedFieldParser._drop_redundant_incomplete_combinations(set())

        # Then
        assert result == set()


class TestBuildCombination:
    def test_builds_tuple_in_topic_theme_sub_theme_order(self):
        # Given
        fields = {
            "topic": "COVID-19",
            "theme": "infectious_disease",
            "sub_theme": "respiratory",
        }

        # When
        combination = CMSSelectedFieldParser._build_combination(fields)

        # Then
        assert combination == ("COVID-19", "infectious_disease", "respiratory")

    def test_missing_keys_default_to_empty_strings(self):
        # Given / When
        combination = CMSSelectedFieldParser._build_combination({"topic": "COVID-19"})

        # Then
        assert combination == ("COVID-19", "", "")

    def test_missing_topic_raises_key_error(self):
        """
        `topic` is mandatory on every plot, so a block without one
        should fail loudly rather than be silently ignored.
        """
        with pytest.raises(KeyError):
            CMSSelectedFieldParser._build_combination({"theme": "infectious_disease"})
