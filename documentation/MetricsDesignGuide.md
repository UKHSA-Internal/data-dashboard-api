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

