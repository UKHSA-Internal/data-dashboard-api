"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

Specifically, this file contains write database logic for the core models only.

NOTE: This code is only for the Alpha. Once we have a data pipeline this code will cease to exist
"""

from typing import Dict, List, Type

import pandas as pd
from django.db import models

from metrics.data.enums import TimePeriod
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
}

frequency = {
    "weekly": TimePeriod.Weekly.value,
    "daily": TimePeriod.Daily.value,
}


DEFAULT_CORE_TIME_SERIES_MODEL = CoreTimeSeries
DEFAULT_CORE_TIME_SERIES_MANAGER = DEFAULT_CORE_TIME_SERIES_MODEL.objects


def check_file(filename: str) -> pd.DataFrame:
    """
    Perform basic checks on the file. eg. does it have the required columns

    Args:
        filename: The name of the file

    Returns:
        The file loaded as a Pandas Dataframe

    Raises:
        Exception if the file is missing, empty or does not have the required columns
    """
    incoming_df = pd.read_csv(filename)
    incoming_df.columns = incoming_df.columns.str.lower()

    required_columns = [
        "parent_theme",
        "child_theme",
        "topic",
        "geography_type",
        "geography",
        "metric_name",
        "stratum",
        "sex",
        "date",
        "metric_value",
    ]

    if set(required_columns).issubset(incoming_df.columns):
        if not incoming_df.empty:
            return incoming_df

    raise ValueError(f"File {filename} has an invalid format or is empty")


def maintain_model(
    incoming_df: pd.DataFrame,
    fields: Dict[str, str],
    model: models.Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
):
    """
    Maintain the individual models that are used in the normalisation of the Core source file
    New values in the source file will be added to the model
    All rows in the source file will get changed from the supplied cell
    value (eg infectious_disease) to the pk for that value. eg 1

    Args:
        incoming_df: This is the entire source file in a DataFrame
        fields: Dictionary of the model field names and the names of the relevant columns in the source file
        model: The model we want to maintain

    Returns:
        incoming_df with the relevant column changed to the primary keys for that model
        So, if the column cotained values like 'infectious_disease' it'll now be, say, 1 (the primary key for 'infectious_disease')
    """

    # From the source file, pull out the unique list of row values for this particular model
    incoming_data: pd.DataFrame = incoming_df[fields.keys()].drop_duplicates()

    # From the model, pull back the existing records along with their pks
    existing_data: pd.DataFrame = pd.DataFrame.from_records(
        model.all().values("pk", *fields.values())
    )

    if existing_data.empty:
        existing_data: pd.DataFrame = pd.DataFrame(columns=list(fields.values()))

    # Left join on incoming_data & existing_data dataframes
    df: pd.DataFrame = pd.merge(
        left=incoming_data,
        right=existing_data,
        how="left",
        left_on=list(fields.keys()),
        right_on=list(fields.values()),
        indicator=True,
    )

    # left_only = those values in the source file which are not present the Model. So, these are new ones
    new_data: List[Dict[str, str]] = (
        df.loc[df["_merge"] == "left_only"][fields.keys()]
        .rename(columns=fields)
        .to_dict("records")
    )

    # Add the new values to the model and pull back the pk for them.
    new_records: List[Dict[str, str]] = [
        {**{"pk": model.create(**data).pk}, **data} for data in new_data
    ]

    # Turn the new records into a dataframe
    added_data: pd.DataFrame = pd.DataFrame(new_records)

    # Add them onto the end of the data that we already had
    all_data: pd.DataFrame = pd.concat([existing_data, added_data])

    # Now join this back onto the original dataframe.
    # So, we're joining the pk and the relevant fields for this model onto the original dataframe
    df = pd.merge(
        left=incoming_df,
        right=all_data,
        how="inner",
        left_on=list(fields.keys()),
        right_on=list(fields.values()),
    )

    # Drop the original column(s) as we're now using the primary keys and not the text representation of them
    # Drop the model field names too (were only here to make debugging easier)
    df = df.drop(columns=[*list(fields.items())[0], *fields.values()])

    # Rename the new columns back to what they are in the source file.
    # So for the parent theme model we are changing it from pk back to parent_theme
    df = df.rename(columns={"pk": list(fields.keys())[0]})

    # At this point the rows for the parent_theme column for example have been changed
    # from "infectious_disease" to, say, 1
    # ie. the Foreign Key for "infectious_disease" in the Theme model.
    return df


def load_core_data(
    filename: str,
    core_time_series_manager: models.Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    core_time_series_model: Type[models.Model] = DEFAULT_CORE_TIME_SERIES_MODEL,
) -> None:
    """
    Load the Core file and maintain the underlying models

    Args:
        filename: The filename of the file we want to load
        core_time_series_manager: The Core Timeseries manager
        core_time_series_model: The model for the Core Timeseries


    Returns:
        None
    """
    incoming_df = check_file(filename=filename)

    df: pd.DataFrame = maintain_model(
        incoming_df=incoming_df,
        fields={"parent_theme": "name"},
        model=Theme.objects,
    )
    df = maintain_model(
        incoming_df=df,
        fields={"child_theme": "name", "parent_theme": "theme_id"},
        model=SubTheme.objects,
    )
    df = maintain_model(
        incoming_df=df,
        fields={"topic": "name", "child_theme": "sub_theme_id"},
        model=Topic.objects,
    )

    # Geography Type appears as both 'nation' and 'Nation' so make them all the same
    df.loc[df["geography_type"] == "nation", "geography_type"] = "Nation"

    df = maintain_model(
        incoming_df=df,
        fields={"geography_type": "name"},
        model=GeographyType.objects,
    )
    df = maintain_model(
        incoming_df=df,
        fields={"geography": "name", "geography_type": "geography_type_id"},
        model=Geography.objects,
    )

    df = maintain_model(
        incoming_df=df,
        fields={"metric_name": "name", "topic": "topic_id"},
        model=Metric.objects,
    )
    df = maintain_model(
        incoming_df=df,
        fields={"stratum": "name"},
        model=Stratum.objects,
    ).copy()

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    df["sex"] = df["sex"].apply(lambda x: sex_options.get(x.lower(), "ALL"))
    df["period"] = df["period"].apply(lambda x: frequency.get(x.lower()))

    # Dataset has NaN values so ignore those rows
    df = df[df["metric_value"].notnull()]

    column_mapping: Dict[str, str] = {
        "period": "period",
        "geography": "geography_id",
        "metric_name": "metric_id",
        "stratum": "stratum_id",
        "sex": "sex",
        "year": "year",
        "epiweek": "epiweek",
        "metric_value": "metric_value",
        "date": "dt",
    }

    df = df[list(column_mapping.keys())]
    df = df.rename(columns=column_mapping)

    records: Dict[str:str] = df.to_dict("records")
    model_instances: List = [core_time_series_model(**record) for record in records]

    core_time_series_manager.bulk_create(model_instances, ignore_conflicts=True)
