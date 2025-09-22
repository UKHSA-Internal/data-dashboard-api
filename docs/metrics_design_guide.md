# Metrics API Design Guide

## Introduction

This guide will outline the current architecture of the Metrics API.

The Metrics API is built on top of [Django](https://docs.djangoproject.com/en/4.1/)
and [Django Rest Framework](https://www.django-rest-framework.org/).

---

## Data model

The data model has been designed as 2 distinct sub-systems:

1. API models. This sub-system represents the **flattened version of the data**. No foreign keys are to be found.
And the raw data is effectively loaded in to a single flat table. 
As a result, one should expect to find a large amount of replicated values.
2. Core models. This sub-system represents the **normalized version of the data**. 
There are a series of foreign key relationships. 
Although this greatly reduced the amount of data needed to be stored.
It does mean that querying the core models will incur penalties from joins depending on the query being performed.
3. RBAC Permission models. This sub-system represents the access control layer of the data. It defines permissions 
and restrictions on who can access specific metrics based on themes, sub-themes, topics, and other attributes. 
These models enforce data security by ensuring that only authorized users can retrieve certain records. 

Note that at the point of data ingestion,
both the **Core models** and **API models** are populated

---

## Chart generation

Currently, the chart generation functionality is bespoke to this codebase.
The chart generation code can be found at `metrics/domain/charts/`.

The [coronavirus-dashboard-pipeline-etl](https://github.com/publichealthengland/coronavirus-dashboard-pipeline-etl)
contains a number of functions which are being used to generate charts of various types 
for the existing coronavirus dashboard. 

This includes:
- Line graphs (with shaded region)
- Heatmaps
- Waffle charts
- Bar charts

As of Sep 2025, the following charts can be generated:

- Line graphs with customizable colour and type (dash/solid)
- Bar charts
- Combination of bar and line types on the same chart
- Simple line graphs 
- Sub plot bar charts
