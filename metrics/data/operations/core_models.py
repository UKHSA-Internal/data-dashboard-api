"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

Specifically, this file contains write database logic for the core models only.
"""

import io
from datetime import datetime
from typing import Dict, List, Type

import pandas as pd
from django.db import models

from metrics.api.enums import TimePeriod
from metrics.data.models.core_models import (
    CoreTimeSeries,
    Geography,
    GeographyType,
    Metric,
    Stratum,
    SubTheme,
    Theme,
    Topic,
)

sex_options = {
    "male": "M",
    "female": "F",
    "all": "ALL",
}


def add_new_model_values(
    incoming_df: pd.DataFrame,
    fields: Dict[str, str],
    model_model: Type[models.Model],
):
    incoming_data: pd.DataFrame = incoming_df[fields.keys()].drop_duplicates()

    existing_data: pd.DataFrame = pd.DataFrame.from_records(
        model_model.objects.all().values("pk", *fields.values())
    )

    if existing_data.empty:
        existing_data: pd.DataFrame = pd.DataFrame(columns=list(fields.values()))

    df: pd.DataFrame = pd.merge(
        left=incoming_data,
        right=existing_data,
        how="left",
        left_on=list(fields.keys()),
        right_on=list(fields.values()),
        indicator=True,
    )

    new_data: List[Dict[str, str]] = (
        df.loc[df["_merge"] == "left_only"][fields.keys()]
        .rename(columns=fields)
        .to_dict("records")
    )

    new_records: List[Dict[str, str]] = [
        {"pk": model_model.objects.create(**data).pk} | data for data in new_data
    ]

    added_data: pd.DataFrame = pd.DataFrame(new_records)
    all_data: pd.DataFrame = pd.concat([existing_data, added_data])

    df = pd.merge(
        left=incoming_df,
        right=all_data,
        how="inner",
        left_on=list(fields.keys()),
        right_on=list(fields.values()),
    )

    df = df.drop(columns=[*list(fields.items())[0], *fields.values()])
    df = df.rename(columns={"pk": list(fields.keys())[0]})
    return df


def load_core_data(filename: str) -> None:
    incoming_df = pd.read_csv(filename)
    df: pd.DataFrame = add_new_model_values(
        incoming_df, {"parent_theme": "name"}, Theme
    )
    df = add_new_model_values(
        df, {"child_theme": "name", "parent_theme": "theme_id"}, SubTheme
    )
    df = add_new_model_values(
        df, {"topic": "name", "child_theme": "sub_theme_id"}, Topic
    )
    df = add_new_model_values(df, {"geography_type": "name"}, GeographyType)
    df = add_new_model_values(
        df, {"geography": "name", "geography_type": "geography_type_id"}, Geography
    )

    df = add_new_model_values(df, {"metric_name": "name", "topic": "topic_id"}, Metric)
    df = add_new_model_values(df, {"stratum": "name"}, Stratum)

    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    df["sex"] = df["sex"].apply(lambda x: sex_options.get(x.lower()))

    df["period"] = TimePeriod.Daily.value

    # Dataset has NaN values so ignore those rows
    df = df[df["metric_value"].notnull()]

    column_mapping: Dict[str, str] = {
        "period": "period",
        "geography": "geography_id",
        "metric_name": "metric_id",
        "stratum": "stratum_id",
        "sex": "sex",
        "metric_value": "metric_value",
        "date": "dt",
    }

    df = df[list(column_mapping.keys())]
    df = df.rename(columns=column_mapping)

    records: Dict[str:str] = df.to_dict("records")
    model_instances: List = [CoreTimeSeries(**record) for record in records]

    CoreTimeSeries.objects.bulk_create(model_instances, ignore_conflicts=True)


def upload_data(data: io.TextIOWrapper) -> None:
    pass
    # for index, line in enumerate(data, 0):
    #     fields: List[str] = line.split(",")
    #     if fields[0] != '"parent_theme"':
    #         try:
    #             _get_or_create_models(fields=fields)
    #         except ValueError:
    #             print(f"Error at line {index}")
