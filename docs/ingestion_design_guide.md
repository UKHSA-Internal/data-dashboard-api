# Ingestion Component Design Guide

## Introduction

This guide will outline the current architecture of the data ingestion component and some of the things to be aware of.

---

## Purpose

The purpose of the ingestion component is to take source data files and consume them and populate the database.
These source data files can be:

- headline      # headline type
- cases         # timeseries type
- coverage      # timeseries type
- deaths        # timeseries type
- healthcare    # timeseries type
- testing       # timeseries type
- vaccinations  # timeseries type

Headline type files are expected to result in `CoreHeadline` records.
All other file types are expected to result in both `CoreTimeSeries` and `APITimeSeries` records.

The ingestion component will also populate any new records on the supporting models. 
For example, a new geography which is not already in the database will result 
in a new `Geography` and maybe a new `GeographyType` record depending on the nature of the data.

---

## Container image

The ingestion workload is packaged and deployed slightly differently to the rest of the backend.

The ingestion workload is packaged via a dedicated `Dockerfile-ingestion` located at the root of the project.
This Dockerfile points at a `requirements-prod-ingestion.txt` file for its project dependencies.
The `requirements-prod-ingestion.txt` file contains a slimmed down version of the project dependencies containing only 
the libraries needed for it to run the ingestion component in isolation.

--- 

## How it works in production

At the time of writing (Jan 2024), the ingestion workload is deployed as an AWS lambda function.
This lambda function subscribes to an AWS Kinesis data stream from which it pulls individual records for ingestion.

When the ingestion lambda reads the record from the Kinesis data stream, 
it passes the record itself into lambda function itself into the function handler.

This is the complete source data for that particular metric/geography/sex/age/stratum combination.

When the lambda function has finished consuming that particular record, it takes the `key` from the record.
That `key` correlates to the corresponding file in the ingest s3 bucket. 
The ingestion lambda function will then move the file from the `in/` folder 
to the `processed/` or the `failed/` folder within the s3 bucket, depending on the outcome of the ingestion process.

---

## Truncated dataset

It should be noted that the `source_data/` directory at the root level of the project contains a number of 
source data files which are used to populate databases in development environments.

These files are run through and handled by the same `Consumer` class 
as the ingestion lambda function in deployed environments.
The only exception being, we consume the test dataset with multiprocessing.

> Note that when running the `boot.sh` command the truncated dataset will be uploaded. 
**All records will be cleared from the database before the upload commences.** 

---

## Metrics interface

Each section of this codebase is designed so that it communicates across explicitly defined boundaries.
In other words, if code which lives in the `ingestion/` directory wants to import things from `metrics/`, 
then it **must** do so via the `MetricsAPIInterface` class.

Note that these boundaries are enforced by the `importlinter` tool which will cause the architectural constraints CI 
build to break, if the rules are violated i.e. if communication occurs outside the defined boundaries.
