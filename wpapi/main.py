import os
import csv
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tortoise import Tortoise, run_async
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from typing import Union

from wpapi import settings, models
from wpapi.models import MultiPathogen

Record = pydantic_model_creator(MultiPathogen)

# This might not be needed as it's initiated in the 'start.sh' script
async def init(local=False):
    await Tortoise.init(
        config=settings.TORTOISE_ORM_LOCAL if local else settings.TORTOISE_ORM
    )
    await Tortoise.generate_schemas()


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/items/raw/")
async def read_items_raw():
    await Tortoise.init(
        config=settings.TORTOISE_ORM_LOCAL,
        modules={'models': ['wpdb.models']}
    )
    saved_items = await MultiPathogen.filter(season="2022-2023").values()
    return saved_items


@app.get("/items/")
async def read_item():
    await Tortoise.init(
        config=settings.TORTOISE_ORM_LOCAL,
        modules={'models': ['wpdb.models']}
    )
    saved_items = await MultiPathogen.filter(season="2022-2023").values()
    output = {
        "week": [],
        "rhinovirus": [],
        "adenovirus": []
    }
    for item in saved_items:
        output["week"].append(item.get("week_key"))
        output["rhinovirus"].append(item.get("rhinovirus_pct"))
        output["adenovirus"].append(item.get("adenovirus_pct"))
    return output


@app.post("/reset/")
async def delete_record(record: Record):
    await Tortoise.init(
        config=settings.TORTOISE_ORM_LOCAL,
        modules={'models': ['wpdb.models']}
    )
    saved_items = await MultiPathogen.all().delete()
    return {}



@app.post("/items/")
async def create_record(record: Record):
    await Tortoise.init(
        config=settings.TORTOISE_ORM_LOCAL,
        modules={'models': ['wpdb.models']}
    )
    multipathogen = await MultiPathogen.create(
        week=record.week,
        year=record.year,
        week_key=record.week,
        publish_date=record.publish_date,
        season=record.season,
        influenza_pct=record.influenza_pct,
        rsv_pct=record.rsv_pct,
        rhinovirus_pct=record.rhinovirus_pct,
        parainfluenza_pct=record.parainfluenza_pct,
        hmpv_pct=record.hmpv_pct,
        adenovirus_pct=record.adenovirus_pct,
        sars_cov_pct=record.sars_cov_pct,
        influenza_a_h3n2_n_pct=record.influenza_a_h3n2_n_pct,
        influenza_a_h1n1_pdm09_n_pct=record.influenza_a_h1n1_pdm09_n_pct,
        influenza_a_not_subtyped_n_pct=record.influenza_a_not_subtyped_n_pct,
        influenza_b_n_pct=record.influenza_b_n_pct
    )
    result = await multipathogen.save()
    return result


@app.get("/testdata/")
async def test_data():
    file_path = os.path.join(settings.BASE_DIR, 'tests', 'fixtures', 'multi_pathogen.csv')

    with open(file_path) as csvfile:
        csv_data = csv.reader(csvfile, delimiter=';')
        rows = []

        for row in csv_data:
            rows.append(row)

    header = rows[0]
    rows = rows[1:]

    # The virus name start form position 5
    index = 5
    data = []

    while index < len(header):
        values = []
        count = []

        for x, row in enumerate(rows):
            count.append(x + 1)

            if row[index]:
                values.append(float(row[index].replace(',', '.')))
            else:
                values.append(0.0)

        data.append(
            {
                "x": count,
                "y": values,
                "name": header[index],
            }
        )

        index += 1

    return data

if __name__ == "__main__":
    from uvicorn import run
    run(app, port=5100)
