from unittest import TestCase, mock

from metrics.data.access.dashboard_metadata import ApplyFormatting
from metrics.data.access.generate_dashboard import format_cell, populate_dashboard


class TestFormatVal(TestCase):
    def test_format_good_int(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="123.45",
            formatting={"number_format": ApplyFormatting.IntNoDP},
        )
        self.assertEqual(actual, "123")

    def test_format_good_pct_with_brackets(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="123.45678",
            formatting={
                "number_format": ApplyFormatting.PctOneDP,
                "add_brackets": True,
            },
        )
        self.assertEqual(actual, "(123.5%)")

    def test_format_good_pct(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="123.45678",
            formatting={"number_format": ApplyFormatting.PctOneDP},
        )
        self.assertEqual(actual, "123.5%")

    def test_format_unknown(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="123.45",
            formatting={"number_format": "unrecognised"},
        )
        self.assertEqual(actual, "unrecognised")

    def test_format_good_negative_int(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="-123.45",
            formatting={"number_format": ApplyFormatting.IntNoDP},
        )
        self.assertEqual(actual, "-123")

    def test_format_good_negative_pct_with_brackets(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="-123.45678",
            formatting={
                "number_format": ApplyFormatting.PctOneDP,
                "add_brackets": True,
            },
        )
        self.assertEqual(actual, "(-123.5%)")

    def test_format_good_negative_pct(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="-123.45678",
            formatting={"number_format": ApplyFormatting.PctOneDP},
        )
        self.assertEqual(actual, "-123.5%")

    def test_format_get_up_arrow(self):
        actual: str = format_cell(
            metric_name="admission",
            metric_value="123.45678",
            formatting={"get_arrow": True},
        )
        self.assertEqual(actual, "up")

    def test_format_get_down_arrow(self):
        actual: str = format_cell(
            metric_name="admission",
            metric_value="-123.45678",
            formatting={"get_arrow": True},
        )
        self.assertEqual(actual, "down")

    def test_format_get_neutral_arrow(self):
        actual: str = format_cell(
            metric_name="deaths",
            metric_value="0",
            formatting={"get_arrow": True},
        )
        self.assertEqual(actual, "neutral")

    def test_format_get_colour_positive_bad(self):
        actual: str = format_cell(
            metric_name="cases",
            metric_value="123.45678",
            formatting={"get_colour": True},
        )
        self.assertEqual(actual, "red")

    def test_format_get_colour_positive_good(self):
        actual: str = format_cell(
            metric_name="vaccination",
            metric_value="123.45678",
            formatting={"get_colour": True},
        )
        self.assertEqual(actual, "green")

    def test_format_get_colour_negative_bad(self):
        actual: str = format_cell(
            metric_name="vaccination",
            metric_value="-123.45678",
            formatting={"get_colour": True},
        )
        self.assertEqual(actual, "red")

    def test_format_get_colour_negative_good(self):
        actual: str = format_cell(
            metric_name="cases",
            metric_value="-123.45678",
            formatting={"get_colour": True},
        )
        self.assertEqual(actual, "green")

    def test_format_get_neutral_colour(self):
        actual: str = format_cell(
            metric_name="admission",
            metric_value="0",
            formatting={"get_colour": True},
        )
        self.assertEqual(actual, "neutral")

    def test_make_absolute(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="-123.45",
            formatting={
                "absolute_number": True,
                "number_format": ApplyFormatting.IntNoDP,
            },
        )
        self.assertEqual(actual, "123")

    def test_format_negative_unknown(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="-123.45",
            formatting={"number_format": "unrecognised"},
        )
        self.assertEqual(actual, "unrecognised")

    def test_format_bad_int(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="no_value",
            formatting={"number_format": ApplyFormatting.IntNoDP},
        )
        self.assertEqual(actual, "no_value")

    def test_format_bad_pct_with_brackets(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="no_value",
            formatting={
                "number_format": ApplyFormatting.PctOneDP,
                "add_brackets": True,
            },
        )
        self.assertEqual(actual, "no_value")

    def test_format_bad_pct(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="no_value",
            formatting={"number_format": ApplyFormatting.PctOneDP},
        )
        self.assertEqual(actual, "no_value")

    def test_format_bad_unknown(self):
        actual: str = format_cell(
            metric_name="ignore",
            metric_value="no_value",
            formatting={"number_format": "unrecognised"},
        )
        self.assertEqual(actual, "no_value")


class TestPopulateDashboard(TestCase):
    @mock.patch(
        "metrics.data.access.generate_dashboard.get_value_from_db",
        return_value={"metric_value": 123.45},
    )
    def test_populate_dashboard_all_fine(self, mock_get_db_value):
        metadata = {
            "coronavirus": [
                {
                    "panel": "Headline",
                    "main_container": "Cases",
                    "secondary_container": "Weekly",
                    "formatting": {"number_format": ApplyFormatting.IntNoDP},
                    "filter": {
                        "topic": "COVID-19",
                        "metric": "new_cases_7days_sum",
                        "geography_type": "Nation",
                        "geography": "England",
                        "stratum": "default",
                        "sex": "ALL",
                    },
                }
            ]
        }

        expected = [
            {
                "panel": "Headline",
                "main_container": "Cases",
                "secondary_container": "Weekly",
                "metric_value": "123",
            }
        ]

        actual = populate_dashboard(topic="coronavirus", metadata=metadata)
        self.assertEqual(actual, expected)
        mock_get_db_value.assert_called_once()

    @mock.patch("metrics.data.access.generate_dashboard.get_value_from_db")
    def test_populate_dashboard_no_filter(self, mock_get_db_value):
        metadata = {
            "coronavirus": [
                {
                    "panel": "Headline",
                    "main_container": "Cases",
                    "secondary_container": "Weekly",
                    "formatting": {"number_format": ApplyFormatting.IntNoDP},
                }
            ]
        }

        populate_dashboard(topic="coronavirus", metadata=metadata)
        mock_get_db_value.assert_not_called()

    @mock.patch(
        "metrics.data.access.generate_dashboard.get_value_from_db",
        return_value={"metric_value": 123.45},
    )
    def test_populate_dashboard_no_formatting(self, mock_get_db_value):
        metadata = {
            "coronavirus": [
                {
                    "panel": "Headline",
                    "main_container": "Cases",
                    "secondary_container": "Weekly",
                    "filter": {
                        "topic": "COVID-19",
                        "metric": "new_cases_7days_sum",
                        "geography_type": "Nation",
                        "geography": "England",
                        "stratum": "default",
                        "sex": "ALL",
                    },
                }
            ]
        }

        expected = [
            {
                "panel": "Headline",
                "main_container": "Cases",
                "secondary_container": "Weekly",
                "metric_value": "123.45",
            }
        ]

        actual = populate_dashboard(topic="coronavirus", metadata=metadata)
        self.assertEqual(actual, expected)
