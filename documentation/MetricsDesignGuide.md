# Metrics API Rolling Design Guide

## Introduction

This guide will outline the current architecture of the Metrics API.

The Metrics API is built on top of [Django](https://docs.djangoproject.com/en/4.1/)
and [Django Rest Framework](https://www.django-rest-framework.org/).

---

## Data ingestion

There is currently no active/automated data ingestion mechanism.
In the future, a drop-off point will need to be agreed with the Data team.
E.g. an AWS s3 bucket location from which the `.csv` metrics data files can be ingested.

Currently, the `PUT upload/` endpoint is being used to load metrics data into the app.
> This endpoint **should not be used in production** and should be removed before Beta private release.

If the data ingestion cannot be integrated with in time for the Beta release, 
then as a minimum it should be moved to a management command.

---

## Data model

The raw data ingested by the system is already > 60k rows. 
A significant portion of the data is redundant and replicated across rows.

The data model has been designed as 2 distinct sub-systems:

1. API models. This sub-system represents the flattened version of the data. No foreign keys are to be found.
And the raw data is effectively loaded in to a single flat table. 
As a result, one should expect to find a large amount of replicated values.
2. Core models. This sub-system represents the normalized version of the data. 
There are a series of foreign key relationships. Although this greatly reduced the amount of data needed to be stored.
It does mean that querying the core models will incur penalties from joins depending on the query being performed.

Note that at the point of data ingestion, the **Core models** are populated.
Once this is done, then the API models can be updated. 
Currently, this is achieved via the management command:

```
python manage.py generate_weekly_time_series
```

---

## Integration with the frontend

The frontend application fetches metrics via the REST API in this app.

---

## Chart generation

Currently, the chart generation functionality is bespoke to this codebase.
The chart generation code can be found at `domain/charts/generation.py`.

The [coronavirus-dashboard-pipeline-etl](https://github.com/publichealthengland/coronavirus-dashboard-pipeline-etl)
contains a number of functions which are being used to generate charts of various types 
for the existing coronavirus dashboard. 

This includes:
- Line graphs (with shaded region)
- Heatmaps
- Waffle charts
- Bar charts

To re-use the chart generation code there are a number of options:

1. Move the chart generation code from the [coronavirus-dashboard-pipeline-etl chart generation module](https://github.com/publichealthengland/coronavirus-dashboard-pipeline-etl/blob/development/db_etl_homepage_graphs/grapher.py)
to instead be its own service. 
With this approach, we can centralise this functionality and have a single source of truth. 
If changes are made to how charts look, then that change can be applied across the board easily. 
Equally, if a new chart type is created, it becomes available to other systems/dashboards by default.

2. Copy the code over into this repo and re-use. 
This is likely the quickest option, but then the UKHSA would then lose the single source of truth benefit 
that comes with option 1. Also note, that there is some engineering time required to decouple the existing code from 
the `coronavirus-dashboard-pipeline-etl` before it can be brought over into this repo.

The works could be phased as follows:
- Use current bespoke chart generation endpoint from `winter-pressures-api`.
- Create chart generation service
- Point `winter-pressures-api` at new chart generation service
- Point `coronavirus-dashboard-pipeline-etl` at new chart generation service.

---

## Current limitations

### Outdated data file

A new daily metrics data file was received on 15th March 2023. 

The team cannot commit to redesigning the data model, 
the API layer and additional querying logic to suit this new data file in time 
for the Alpha release (end of March 2023).

As such, this work will need to be completed in April 2023 to support the new data file provided.

### Data ingestion

Currently, the data is being ingested via the `PUT upload/` endpoint. 
This endpoint is now deprecated and will need to be removed.

An integration point will need to be agreed with the UKHSA data team so that this application can consume
data files produced by the UKHSA ETL pipeline.

Note that this file is always provided in its entirety. With years worth of data which is unchanged.
This is most likely costing a considerable sum of money for cloud storage costs.

In the future, this should be altered so that a data file is provided which only shows the most recent month 
of data. Since data prior to this is unlikely to change.

