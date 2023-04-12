"""
Metadata for the Dashboard.

** This implementation is only a temporary solution intended for the Alpha release **

The plan is that this data will be maintained within the CMS.
This will eliminate the need for a backend code release to change what is displayed
  on the Dashboard
"""

from enum import Enum


class ApplyFormatting(str, Enum):
    """The formatting to apply to the metric value

    Is basically just the specification to pass to the Python format function
    """

    IntNoDP = "{0:,.0f}"
    PctOneDP = "{0:,.1f}%"

    def __str__(self) -> str:
        return self.value


"""
Metadata Format:

    One dictionary per panel element

    panel: Headline or Tile
        Describes where it is to be displayed on the dashboard.
            Headline is the full width panel.
            Tile is one of the tiles

    main_container: Various
        Which main container on the particular panel this data should be loaded into

    secondary_container: Various
        Which sub-container on this particulaer panel this data should be loaded into

    formatting: See format_cell function in generate_dashboard

    filter: The filters to use when pulling back data from the APITimeSeries Model
        So, "metric": "new_cases_7days_sum" will pull back 
          data for the new_cases_7days_sum metric.
        The filters are on an AND basis as opposed to an OR basis

    fields: The fields to pull back from the APITimeSeries Model

"""
coronavirus_headline = [
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
    },
    {
        "panel": "Headline",
        "main_container": "Cases",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Cases",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Cases",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Cases",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Deaths",
        "secondary_container": "Weekly",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_sum",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Deaths",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Deaths",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Deaths",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Deaths",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "Patients admitted",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_admissions_7days",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_admissions_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_admissions_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_admissions_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_admissions_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Vaccinations",
        "secondary_container": "Autumn Booster",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "latest_total_vaccinations_autumn22",
            "geography_type": "Nation",
            "geography": "England",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Vaccinations",
        "secondary_container": "Percentage uptake (%)",
        "formatting": {"number_format": ApplyFormatting.PctOneDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "latest_vaccinations_uptake_autumn22",
            "geography_type": "Nation",
            "geography": "England",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Testing",
        "secondary_container": "Virus tests positivity (%)",
        "formatting": {"number_format": ApplyFormatting.PctOneDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "positivity_7days_latest",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
]


coronavirus_tiles = [
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "Positive tests reported in England",
    },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "Up to and including {}",
        "fields": ["dt"],
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_daily",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_sum",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "change",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_cases_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "Deaths with COVID-19 on the death Certificate in England",
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "Up to and including {}",
        "fields": ["dt"],
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_daily",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_sum",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "change",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "new_deaths_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
]


influenza_headline = [
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "Hospital admission rate (per 100,000)",
        "formatting": {
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_latest",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Healthcare",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Testing",
        "secondary_container": "Virus tests positivity (%)",
        "formatting": {
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_positivity_latest",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
]

influenza_tiles = [
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "Weekly hospital admission rates for Influenza",
    },
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "Up to and including {}",
        "fields": ["dt"],
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "Last 7 days",
        "formatting": {
            "absolute_number": True,
            "number_format": ApplyFormatting.IntNoDP,
        },
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_latest",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "change",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "percentage_change",
        "formatting": {
            "number_format": ApplyFormatting.PctOneDP,
            "add_brackets": True,
        },
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "colour",
        "formatting": {"get_colour": True},
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Healthcare",
        "secondary_container": "arrow",
        "formatting": {"get_arrow": True},
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_hospital_admissions_rate_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Tile",
        "main_container": "Testing",
        "secondary_container": "Weekly positivity",
    },
    {
        "panel": "Tile",
        "main_container": "Testing",
        "secondary_container": "Up to and including {}",
        "fields": ["dt"],
        "filter": {
            "topic": "Influenza",
            "metric": "weekly_positivity",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
]

# Pull each virus type into one
virus_metadata = {
    "COVID-19": coronavirus_headline + coronavirus_tiles,
    "Influenza": influenza_headline + influenza_tiles,
}
