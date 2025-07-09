from unittest import mock

from cms.metrics_interface import field_choices_callables, interface
from cms.metrics_interface.field_choices_callables import (
    DUAL_CHART_SECONDARY_CATEGORY_FILTER_LIST,
)
from metrics.domain.charts.colour_scheme import RGBAChartLineColours

from metrics.domain.charts.common_charts.plots.line_multi_coloured.properties import (
    ChartLineTypes,
)
from metrics.domain.common.utils import ChartAxisFields
from metrics.interfaces.charts.single_category_charts.access import ChartTypes
from tests.fakes.models.queryset import FakeQuerySet


class TestGetAllUniqueMetricNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_unique_metric_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_metric_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique metric names
        When `get_all_unique_metric_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_metric_names = ["COVID-19_deaths_ONSRollingMean"]
        mocked_get_all_unique_metric_names.return_value = retrieved_unique_metric_names

        # When
        unique_metric_names = field_choices_callables.get_all_unique_metric_names()

        # Then
        assert unique_metric_names == [(x, x) for x in retrieved_unique_metric_names]


class TestGetAlLTimeSeriesMetricNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_timeseries_metric_names")
    def test_delegates_calls_correctly(
        self, mocked_get_all_timeseries_metric_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique timeseries metric names
        When `get_all_timeseries_metric_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_metric_names = ["COVID-19_deaths_ONSRollingMean"]
        mocked_get_all_timeseries_metric_names.return_value = (
            retrieved_unique_metric_names
        )

        # When
        unique_metric_names = field_choices_callables.get_all_timeseries_metric_names()

        # Then
        assert unique_metric_names == [(x, x) for x in retrieved_unique_metric_names]


class TestGetAllHeadlineMetricNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_headline_metric_names")
    def test_delegates_calls_correctly(
        self, mocked_get_all_headline_metric_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns headline metric names
        When `get_all_headline_metric_names()` is called
        Then the headline metric names are returned as a list of 2-item tuples
        """
        retrieved_headline_metric_names = ["COVID-19_headline_cases_7DayTotals"]
        mocked_get_all_headline_metric_names.return_value = (
            retrieved_headline_metric_names
        )

        # When
        headline_metric_names = field_choices_callables.get_all_headline_metric_names()

        # Then
        assert headline_metric_names == [
            (x, x) for x in retrieved_headline_metric_names
        ]


class TestGetAllUniqueChangeTypeMetricNames:
    @mock.patch.object(
        interface.MetricsAPIInterface, "get_all_unique_change_type_metric_names"
    )
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_change_type_metric_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique metric names
        When `get_all_unique_change_type_metric_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_change_type_metric_names = ["COVID-19_deaths_ONSRollingMean"]
        mocked_get_all_unique_change_type_metric_names.return_value = (
            retrieved_unique_change_type_metric_names
        )

        # When
        unique_change_type_metric_names = (
            field_choices_callables.get_all_unique_change_type_metric_names()
        )

        # Then
        assert unique_change_type_metric_names == [
            (x, x) for x in retrieved_unique_change_type_metric_names
        ]


class TestGetAllUniquePercentChangeTypeMetricNames:
    @mock.patch.object(
        interface.MetricsAPIInterface, "get_all_unique_percent_change_type_names"
    )
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_percent_change_type_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique metric names
        When `get_all_unique_percent_change_type_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_change_percent_type_metric_names = [
            "COVID-19_deaths_ONSRollingMean"
        ]
        mocked_get_all_unique_percent_change_type_names.return_value = (
            retrieved_unique_change_percent_type_metric_names
        )

        # When
        unique_change_percent_type_metric_names = (
            field_choices_callables.get_all_unique_percent_change_type_names()
        )

        # Then
        assert unique_change_percent_type_metric_names == [
            (x, x) for x in retrieved_unique_change_percent_type_metric_names
        ]


class TestGetChartTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_chart_types")
    def test_delegates_call_correctly(self, mocked_get_chart_types: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns chart types
        When `get_chart_types()` is called
        Then the chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_chart_types = ChartTypes.choices()
        mocked_get_chart_types.return_value = retrieved_chart_types

        # When
        chart_types = field_choices_callables.get_chart_types()

        # Then
        assert chart_types == retrieved_chart_types


class TestHeadlineChartTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_headline_chart_types")
    def test_delegates_call_correctly(
        self, mocked_get_headline_chart_types: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns headline chart types
        When `get_headline_chart_types()` is called
        Then the chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_headline_chart_types = ChartTypes.choices()
        mocked_get_headline_chart_types.return_value = retrieved_headline_chart_types

        # When
        headline_chart_types = field_choices_callables.get_headline_chart_types()

        # Then
        assert headline_chart_types == retrieved_headline_chart_types


class TestGetChartAxis:
    @mock.patch.object(interface.MetricsAPIInterface, "get_chart_axis_choices")
    def test_delegates_call_correctly(
        self, mocked_get_chart_axis_choices: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns Chart Axis Fields
        When `get_possible_axis_choices()` is called
        Then the chart Axes are returned as a list of 2-item tuples
        """
        # Given
        retrieved_chart_axis_choices = ChartAxisFields.choices()
        mocked_get_chart_axis_choices.return_value = retrieved_chart_axis_choices

        # When
        chart_axis_choices = field_choices_callables.get_possible_axis_choices()

        # Then
        assert chart_axis_choices == retrieved_chart_axis_choices


class TestGetDualChartCategoryChoices:
    @mock.patch.object(interface.MetricsAPIInterface, "get_chart_axis_choices")
    def test_delegates_call_correctly(
        self, mocked_get_dual_chart_category_choices: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns dual chart category choices
        When `get_dual_chart_category_choices()` is called
        Then the dual chart category choices are returned as a list of 2-item tuples
        """
        # Given
        retrieved_dual_chart_category_choices = [
            (choice, choice)
            for choice, choice in ChartAxisFields.choices()
            if choice not in DUAL_CHART_SECONDARY_CATEGORY_FILTER_LIST
        ]
        mocked_get_dual_chart_category_choices.return_value = (
            retrieved_dual_chart_category_choices
        )

        # When
        dual_category_chart_choices = (
            field_choices_callables.get_dual_chart_secondary_category_choices()
        )

        # Then
        assert dual_category_chart_choices == retrieved_dual_chart_category_choices


class TestGetDualCategoryChartTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_dual_category_chart_types")
    def test_delegates_call_correctly(
        self, mocked_get_dual_category_chart_types: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns dual category chart types
        When `get_dual_category_chart_types()` is called
        Then the dual category chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_dual_category_chart_types = ChartTypes.dual_category_chart_options()
        mocked_get_dual_category_chart_types.return_value = (
            retrieved_dual_category_chart_types
        )

        # When
        dual_category_chart_types = (
            field_choices_callables.get_dual_category_chart_types()
        )

        # Then
        assert dual_category_chart_types == retrieved_dual_category_chart_types


class TestGetChartLineTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_chart_line_types")
    def test_delegates_call_correctly(
        self, mocked_get_chart_line_types: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns chart line types
        When `get_chart_line_types()` is called
        Then the chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_chart_line_types = ChartLineTypes.choices()
        mocked_get_chart_line_types.return_value = retrieved_chart_line_types

        # When
        chart_line_types = field_choices_callables.get_chart_line_types()

        # Then
        assert chart_line_types == retrieved_chart_line_types


class TestGetColours:
    @mock.patch.object(interface.MetricsAPIInterface, "get_colours")
    def test_delegates_call_correctly(self, mocked_get_colours: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns available RGBA colours
        When `get_colours()` is called
        Then the colours are returned as a list of 2-item tuples
        """
        # Given
        retrieved_colours = RGBAChartLineColours.choices()
        mocked_get_colours.return_value = retrieved_colours

        # When
        colours = field_choices_callables.get_colours()

        # Then
        assert colours == retrieved_colours


class TestGetAllTopicNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_topic_names")
    def test_delegates_call_correctly(self, mocked_get_all_topic_names: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns topic names
        When `get_all_topic_names()` is called
        Then the topic names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_topic_names = ["COVID-19", "Influenza"]
        mocked_get_all_topic_names.return_value = retrieved_topic_names

        # When
        topic_names = field_choices_callables.get_all_topic_names()

        # Then
        assert topic_names == [(x, x) for x in retrieved_topic_names]


class TestGetListOfAllTopicNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_topic_names")
    def test_returns_names_in_the_correct_format(
        self, mocked_get_a_list_of_all_topic_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns topic names.
        When `get_a_list_of_all_topic_names()` is called.
        Then the topic names are returned as a list of strings.
        """
        # Given
        retrieved_topic_names = ["COVID-19", "Influenza"]
        retrieved_topic_names_queryset = FakeQuerySet(retrieved_topic_names)
        mocked_get_a_list_of_all_topic_names.return_value = (
            retrieved_topic_names_queryset
        )

        # When
        topic_names = field_choices_callables.get_a_list_of_all_topic_names()

        # Then
        assert topic_names == retrieved_topic_names


class TestGetAllStratumNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_stratum_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_stratum_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns stratum names
        When `get_all_stratum_names()` is called
        Then the stratum names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_stratum_names = ["default"]
        mocked_get_all_stratum_names.return_value = retrieved_stratum_names

        # When
        stratum_names = field_choices_callables.get_all_stratum_names()

        # Then
        assert stratum_names == [(x, x) for x in retrieved_stratum_names]


class TestGetAllGeographyNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_geography_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_geography_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns geography names
        When `get_all_geographies()` is called
        Then the geography names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_geography_names = ["London", "Yorkshire and Humber"]
        mocked_get_all_geography_names.return_value = retrieved_geography_names

        # When
        geographies_names = field_choices_callables.get_all_geography_names()

        # Then
        assert geographies_names == [(x, x) for x in retrieved_geography_names]


class TestGetAllGeographyNamesAndCodesForAlerts:
    @mock.patch.object(
        interface.MetricsAPIInterface,
        "get_all_geography_names_and_codes_by_geography_type",
    )
    def test_delegates_call_correctly(
        self,
        mocked_get_all_geography_names_and_codes_by_geography_type: mock.MagicMock,
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns geography types and codes
        When `get_all_geography_names_and_codes_for_alerts()` is called
        Then an empty list is returned for the stubbed call.
        """
        # Given
        retrieved_geography_names_and_codes = []
        mocked_get_all_geography_names_and_codes_by_geography_type.return_value = (
            retrieved_geography_names_and_codes
        )

        # When
        geography_names_and_codes = (
            field_choices_callables.get_all_geography_names_and_codes_for_alerts()
        )

        # Then
        assert geography_names_and_codes == retrieved_geography_names_and_codes


class TestGetAllGeographyTypeNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_geography_type_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_geography_type_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns geography type names
        When `get_all_geography_types()` is called
        Then the geography names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_geography_type_names = ["London", "Yorkshire and Humber"]
        mocked_get_all_geography_type_names.return_value = (
            retrieved_geography_type_names
        )

        # When
        geography_type_names = field_choices_callables.get_all_geography_type_names()

        # Then
        assert geography_type_names == [(x, x) for x in retrieved_geography_type_names]


class TestGetAllSexNames:
    def test_returns_correct_values(self):
        """
        Given no input
        When `get_all_sex_names()` is called
        Then the correct sex names are returned
            as a list of 2-item tuples
        """
        # Given / When
        sex_names = field_choices_callables.get_all_sex_names()

        # Then
        assert sex_names == [("all", "all"), ("f", "f"), ("m", "m")]


class TestGetAllAgeNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_age_names")
    def test_delegates_call_correctly(self, mocked_get_all_age_names: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns age names
        When `get_all_age_names()` is called
        Then the age names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_age_names = [
            "40-44",
            "45-54",
        ]
        mocked_get_all_age_names.return_value = retrieved_age_names

        # When
        all_age_names = field_choices_callables.get_all_age_names()

        # Then
        assert all_age_names == [(x, x) for x in retrieved_age_names]


class TestGetAllThemeNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_theme_names")
    def test_delegates_call_correctly(self, mocked_get_all_theme_names: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns theme names
        When `get_all_theme_names()` is called
        Then the theme names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_theme_names = [
            "infectious_disease",
            "extreme-event",
        ]
        mocked_get_all_theme_names.return_value = retrieved_theme_names

        # When
        all_theme_names = field_choices_callables.get_all_theme_names()

        # Then
        assert all_theme_names == [(x, x) for x in retrieved_theme_names]


class TestGetAllSubThemeNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_sub_theme_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_sub_theme_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns sub theme names
        When `get_all_sub_theme_names()` is called
        Then the sub theme names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_sub_theme_names = [
            "respiratory",
            "weather_alert",
        ]
        mocked_get_all_sub_theme_names.return_value = retrieved_sub_theme_names

        # When
        all_sub_theme_names = field_choices_callables.get_all_sub_theme_names()

        # Then
        assert all_sub_theme_names == [(x, x) for x in retrieved_sub_theme_names]


class TestGetAllUniqueSubThemeNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_unique_sub_theme_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_sub_theme_names: mock.MagicMock
    ):
        """f
        Given an instance of the `MetricsAPIInterface` which returns unique sub theme names
        When `get_all_unique_sub_theme_names()` is called
        Then the unique sub theme names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_sub_theme_names = [
            "respiratory",
            "weather_alert",
        ]
        mocked_get_all_unique_sub_theme_names.return_value = (
            retrieved_unique_sub_theme_names
        )

        # When
        all_unique_sub_theme_names = (
            field_choices_callables.get_all_unique_sub_theme_names()
        )

        # Then
        assert all_unique_sub_theme_names == [
            (x, x) for x in retrieved_unique_sub_theme_names
        ]


class TestSimplifiedChartTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_simplified_chart_types")
    def test_delegates_call_correctly(
        self, mocked_get_simplified_chart_types: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns simplified chart types
        When `get_simplified_chart_types()` is called
        Then the chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_chart_types = ChartTypes.selectable_simplified_chart_choices()
        mocked_get_simplified_chart_types.return_value = retrieved_chart_types

        # When
        simplified_chart_types = field_choices_callables.get_simplified_chart_types()

        # Then
        assert simplified_chart_types == retrieved_chart_types


class TestGetAllSubcategoryChoices:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_age_names")
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_stratum_names")
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_geography_names")
    def test_delegates_call_correctly(
        self,
        mocked_get_all_age_names: mock.MagicMock,
        mocked_get_all_stratum_names: mock.MagicMock,
        mocked_get_all_geography_names: mock.MagicMock,
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns subcategory choices
        When `get_all_subcategory_choices()` is called
        Then the subcategory choices are returned as a list of 2-item tuples
        """
        # Given
        mocked_get_all_sex_names = ["all", "f", "m"]
        mocked_get_all_age_names.return_value = ["00-04", "05-11"]
        mocked_get_all_stratum_names.return_value = ["default"]
        mocked_get_all_geography_names.return_value = ["London", "Yorkshire and Humber"]

        # When
        retrieved_subcategory_choices = (
            field_choices_callables.get_all_subcategory_choices()
        )
        expected_subcategory_choices = [
            (field, field)
            for field in [
                *mocked_get_all_geography_names.return_value,
                *mocked_get_all_sex_names,
                *mocked_get_all_stratum_names.return_value,
                *mocked_get_all_age_names.return_value,
            ]
        ]

        # Then
        assert retrieved_subcategory_choices == expected_subcategory_choices


class TestGetAllGeographiesByType:
    @mock.patch(
        "cms.metrics_interface.field_choices_callables.get_all_geography_type_names"
    )
    @mock.patch.object(
        interface.MetricsAPIInterface, "get_all_geography_names_by_geography_type"
    )
    def test_delegates_call_correctly(
        self,
        mocked_get_all_geography_names_by_geography_type: mock.MagicMock,
        mocked_get_all_geography_type_names: mock.MagicMock,
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns geography names by type
        When `get_all_geography_names_by_geography_type` is called
        Then the geography names are returned as a dictionary where the geography type key
            has a list of 2-item tuples for its value.
        """
        # Given
        mocked_get_all_geography_type_names.return_value = [
            ("FakeGeographyTypeOne", "FakeGeographyTypeOne"),
            ("FakeGeographyTypeTwo", "FakeGeographyTypeTwo"),
        ]
        mocked_get_all_geography_names_by_geography_type.side_effect = [
            ["FakeGeography1", "FakeGeography2"],
            ["FakeGeography3", "FakeGeography4"],
        ]

        # When
        retrieved_geography_choices_grouped_by_type = (
            field_choices_callables.get_all_geography_choices_grouped_by_type()
        )
        expected_geography_choices_grouped_by_type = {
            "FakeGeographyTypeOne": [
                ("FakeGeography1", "FakeGeography1"),
                ("FakeGeography2", "FakeGeography2"),
            ],
            "FakeGeographyTypeTwo": [
                ("FakeGeography3", "FakeGeography3"),
                ("FakeGeography4", "FakeGeography4"),
            ],
        }

        # Then
        assert (
            retrieved_geography_choices_grouped_by_type
            == expected_geography_choices_grouped_by_type
        )


class TestGetAllSubcategoryChoicesGroupedByCategories:
    @mock.patch(
        "cms.metrics_interface.field_choices_callables.get_all_geography_choices_grouped_by_type"
    )
    @mock.patch("cms.metrics_interface.field_choices_callables.get_all_stratum_names")
    @mock.patch("cms.metrics_interface.field_choices_callables.get_all_sex_names")
    @mock.patch("cms.metrics_interface.field_choices_callables.get_all_age_names")
    def test_receives_subcategory_choices_grouped_by_category(
        self,
        mocked_get_all_age_names: mock.MagicMock,
        mocked_get_all_sex_names: mock.MagicMock,
        mocked_get_all_stratum_names: mock.MagicMock,
        mocked_all_geography_choices_grouped_by_type: mock.MagicMock,
    ):
        """f
        Given an instance of the `MetricsAPIInterface` which returns subcategory choices
        When `get_all_subcategory_choices_grouped_by_categories` is called
        Then a dictionary is returned containing the subcategory choices grouped by category
        """
        # Given
        mocked_get_all_age_names.return_value = [("00-04", "00-04"), ("05-11", "05-11")]
        mocked_get_all_sex_names.return_value = [("all", "all"), ("m", "m"), ("f", "f")]
        mocked_get_all_stratum_names.return_value = [("default", "default")]
        mocked_all_geography_choices_grouped_by_type.return_value = [
            ("London", "London"),
            ("Leeds", "Leeds"),
        ]

        # When
        received_categories = (
            field_choices_callables.get_all_subcategory_choices_grouped_by_categories()
        )
        expected_subcategory_choices = {
            "age": mocked_get_all_age_names(),
            "sex": mocked_get_all_sex_names(),
            "stratum": mocked_get_all_stratum_names(),
            "geography": mocked_all_geography_choices_grouped_by_type(),
        }

        # Then
        assert received_categories == expected_subcategory_choices
