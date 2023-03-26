from enum import Enum


class ApplyFormatting(str, Enum):
    IntNoDP = "{0:,.0f}"
    PctOneDP = "{0:,.1f}%"

    def __str__(self) -> str:
        return self.value


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
        "panel": "Headline",
        "main_container": "Cases",
        "secondary_container": "percentage_change",
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
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
        "secondary_container": "arrow",
        "filter": {
            # "topic": "COVID-19",
            # "metric": null,
            # "geography_type": null,
            # "geography": null,
            # "stratum": null,
            # "sex": null,
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
        "formatting": [ApplyFormatting.IntNoDP],
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
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
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
        "secondary_container": "arrow",
        # "filter": {
        #     "topic": "COVID-19",
        #     "metric": null,
        #     "geography_type": null,
        #     "geography": null,
        #     "stratum": null,
        #     "sex": null,
        # },
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
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
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
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
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
        "secondary_container": "arrow",
        "filter": {
            # "topic": "COVID-19",
            # "metric": null,
            # "geography_type": null,
            # "geography": null,
            # "stratum": null,
            # "sex": null,
        },
    },
    {
        "panel": "Headline",
        "main_container": "Vaccinations",
        "secondary_container": "Spring Booster",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "latest_total_vaccinations_autumn22",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Vaccinations",
        "secondary_container": "Summer Booster",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "latest_vaccination_uptake_autumn22",
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
    {
        "panel": "Headline",
        "main_container": "Testing",
        "secondary_container": "Last 7 days",
        "formatting": {"number_format": ApplyFormatting.IntNoDP},
        "filter": {
            "topic": "COVID-19",
            "metric": "positivity_7days_change",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Testing",
        "secondary_container": "percentage_change",
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
        "filter": {
            "topic": "COVID-19",
            "metric": "positivity_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    },
    {
        "panel": "Headline",
        "main_container": "Testing",
        "secondary_container": "arrow",
        "filter": {
            # "topic": "COVID-19",
            # "metric": null,
            # "geography_type": null,
            # "geography": null,
            # "stratum": null,
            # "sex": null,
        },
    },
]


coronavirus_tiles = [
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "People tested positive in England",
    },
    # pull values from db
    # {
    #     "panel": "Tile",
    #     "main_container": "Cases",
    #     "secondary_container": "Up to and including 25 February 2023",
    # },
    {
        "panel": "Tile",
        "main_container": "Cases",
        "secondary_container": "Last 7 days",
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
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
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
        "secondary_container": "arrow",
    },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "Deaths with COVID-19 on the death Certificate in England",
    },
    # pull values from db
    # {
    #     "panel": "Tile",
    #     "main_container": "Deaths",
    #     "secondary_container": "Up to and including 25 February 2023",
    # },
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "Last 7 days",
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
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
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
        "secondary_container": "arrow",
        "filter": {
            # "topic": "COVID-19",
            # "metric": null,
            # "geography_type": null,
            # "geography": null,
            # "stratum": null,
            # "sex": null,
        },
    },
]


influenza_headline = []

influenza_tiles = [
    {
        "panel": "Tile",
        "main_container": "Deaths",
        "secondary_container": "percentage_change",
        "formatting": {"number_format": ApplyFormatting.PctOneDP, "add_brackets": True},
        "filter": {
            "topic": "Influenza",
            "metric": "new_deaths_7days_change_percentage",
            "geography_type": "Nation",
            "geography": "England",
            "stratum": "default",
            "sex": "ALL",
        },
    }
]


virus_metadata = {
    "coronavirus": coronavirus_headline + coronavirus_tiles,
    "influenza": influenza_headline + influenza_tiles,
}
