# REST Schema Document

## Introduction

This document details the existing and planned endpoints. The schema documentation available at the `/redoc/` or `/swagger/` endpoints shows the current endpoints and in time everything outlined below will be visible there at which point this document can be deleted.

---

## Deprecated endpoints

The following endpoints were built for the Alpha release and as such are now deprecated

- `/api/pages/` Retrieve CMS page content. Will be replaced by a dynamic equivalent. See below

- `/api/stats/` Retrieve all statistics for a particular topic. Will be replaced by a dynamic equivalent. See below

- `/timeseries/` Retrieve timeseries data for the specified parameters. Will be replaced by a dynamic equivalent. See below

- `/charts/` Retrieve a chart (in png/jpg format) for a given topic and category. Will be replaced by a dynamic equivalent. See below

- `/tabular_data/` Retrieve summary chart data in tabular format. Will be replaced by a dynamic equivalent. See below

- `/upload/` will not be replaced

<br />

---
## Internal Use Only Endpoints

The following endpoints are for admin/internal use only

- `/admin/` To administer the Django site

- `/cms-admin/` For maintaining the CMS content

- `/health/` For checking the health of the site

<br />

## Active Endpoints

--- 
<br />

These endpoints are in active development although the way they're called and the results they return are essentially fixed. The following endpoints are used to construct a page similar to this:

![Figure 1](SamplePage.jpg)

- `/api/pages/v2/`

This endpoint will retrieve from the CMS the complete page content for the chosen topic to enable the construction of the above page. The retrieved content will include the associated information to enable the user to construct the full list of items on the page. For example, to construct the requests for the metrics and graphs.


Example Response:

```
[
    {"type": "text", "body": "<body>\n Data and insights from the UKHSA on respiratory viruses\n</body>"},
    {"type": "text", "body": "<h2>Coronavirus</h2>\n The UKHSA dashboard for data and insights on coronavirus."},
    {
        "type": "headline_column",
        "body": "<body><h3>Cases</h3>",
        "headline": [
            {
                "type": "basic",
                "body": "<b>Weekly</b>",
                "params": {
                    "topic": "COVID-19",
                    "metric": "new_cases_7days_sum",
                    "geography_type": "Nation",
                    "geography": "England",
                    "stratum": "default",
                    "sex": "ALL",
                },
            },
            {
                "type": "trend",
                "body": "<b>Last 7 days</b>",
                "params": {
                    "topic": "COVID-19",
                    "metric": "new_cases_7days_change",
                    "geography_type": "Nation",
                    "geography": "England",
                    "stratum": "default",
                    "sex": "ALL",
                },
            },
        ],
    },
    {"type": "headline_column", "body": "<body><h3>Deaths</h3>", ...},
    {"type": "headline_column", "body": "<body><h3>Healthcare</h3>", ...},
    {"type": "headline_column", "body": "<body><h3>Vaccines</h3>", ...},
    {"type": "headline_column", "body": "<body><h3>Testing</h3>", ...},
    {
        "type": "chart_card",
        "body": "<body><h3>Cases</h3>\n <b>Positive tests reported in England</b>\n Up to and including 25 February 2023</body>",
        "chart": {
            "params": {
                "topic": "COVID-19",
                "metric": "new_cases_daily",
                "chart_type": "line_with_shaded_section",
                "date_from": "2022-10-01",
            },
            "body": "",
        },
        "tabular": {
            "params": {
                "topic": "COVID-19",
                "metric": "new_cases_daily",
                "geography_type": "Nation",
                "geography": "England",
                "stratum": "default",
                "sex": "ALL",
                "date_from": "2022-10-01",
            },
            "body": "",
        },
        "headline": [
            {
                "type": "basic",
                "body": "<b>Last 7 days</b>",
                "params": {
                    "topic": "COVID-19",
                    "metric": "new_cases_7days_sum",
                    "geography_type": "Nation",
                    "geography": "England",
                    "stratum": "default",
                    "sex": "ALL",
                },
            },
            {
                "type": "trend",
                "body": "",
                "params": {
                    "topic": "COVID-19",
                    "metric": "new_cases_7days_change",
                    "geography_type": "Nation",
                    "geography": "England",
                    "stratum": "default",
                    "sex": "ALL",
                },
            },
        ],
    },
]

```

As can be seen above there are several sections in the response:

### The `headline_column` section is used to construct the parematers for calls to the `/api/headlines/v2/` endpoint.

```
    {
        "type": "headline_column",
        "body": "<body><h3>Cases</h3>",
        "headline": [
          {
                "type": "basic",
                "body": "<b>Weekly</b>",
                "params": {
                    "topic": "COVID-19",
                    "metric": "new_cases_7days_sum",
                    "geography_type": "Nation",
                    "geography": "England",
                    "stratum": "default",
                    "sex": "ALL",
                },
            },
            {
                "type": "trend",
                "body": "<b>Last 7 days</b>",
                "params": {
                    "topic": "COVID-19",
                    "metric": "new_cases_7days_change",
                    "geography_type": "Nation",
                    "geography": "England",
                    "stratum": "default",
                    "sex": "ALL",
                },
            },
        ],
    },``
```

See the `params` dictionary in the `COVID-19` `new_cases_7days_sum` section:

                 "topic": "COVID-19",
                 "metric": "new_cases_7days_sum",
                 "geography_type": "Nation",
                 "geography": "England",
                 "stratum": "default",
                 "sex": "ALL",

These are the parameters to pull back data for Weekly Covid Cases













- `/api/tabular/v2/`

This endpoint will retrieve summary chart data in tabular format. The parameters for the query will be detailed in the output from the call to the `/api/pages/v2/` endpoint.

- `/api/headlines/v2/`

This endpoint will "Headline" information. The parameters for the query will be detailed in the output from the call to the `/api/pages/v2/` endpoint.





- `/api/trends/v2/`

Tile information

- `/api/downloads/v2/`

Design yet to be discussed






### `/swagger/`

### REST API Documentation. Alternative to Redocly (see below)


REST API Documentation. Alternative to Redocly (see below)


- `GET`

comment got get

--- 
### `/redoc/`

REST API Documentation. Alternative to Swagger (see above)

--- 

`/api/charts/v2/{topic}/{metric}/{chart-type}/{start_date}/`

`/api/charts/v2/{topic}/{metric}/{chart-type}/{start_date}/`


Charts endpoint.



Mandatory parameters


- `GET`

comment got get