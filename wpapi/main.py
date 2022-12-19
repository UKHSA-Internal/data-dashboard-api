import os
import csv
import logging
from typing import Union

import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.handlers import disable_signing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile
from pydantic import BaseModel
from tortoise import Tortoise, run_async
from tortoise.contrib.pydantic import pydantic_model_creator

from wpapi import settings
from wpapi.models import MultiPathogen

Record = pydantic_model_creator(MultiPathogen)
logging.basicConfig(level=logging.DEBUG)

AWS_REGION = "eu-west-2"
S3_BUCKET_NAME = "wp-incoming-dev"
FILENAME = "winter.csv"


# This might not be needed as it's initiated in the 'start.sh' script
async def init(local=False):
    await Tortoise.init(
        config=settings.TORTOISE_ORM_LOCAL if local else settings.TORTOISE_ORM
    )
    await Tortoise.generate_schemas()


app = FastAPI(debug=True)

origins = [
    "http://wp-lb-1-289742994.eu-west-2.elb.amazonaws.com",
    "http://wp-lb-frontend-1239290931.eu-west-2.elb.amazonaws.com",
    "http://localhost:3000",
]

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
        config=settings.TORTOISE_ORM,
        modules={'models': ['wpdb.models']}
    )
    saved_items = await MultiPathogen.filter(season="2022-2023").values()
    return saved_items


@app.get("/")
async def root():
    print("This is the root end point")
    logging.debug("This is the root end point")
    return {"message": "Hello World"}


@app.get("/items/")
async def read_items():
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
        modules={'models': ['wpdb.models']}
    )
    saved_items = await MultiPathogen.filter(season="2021-2022").values()
    output = {
        "week": [],
        "dates": [],
        "Influenza": [],
        "RSV": [],
        "SARS-CoV-2": [],
        "Adenovirus": [],
        "Parainfluenza": [],
        "Rhinovirus": [],
        "hMPV": []
    }
    for item in saved_items:
        output["week"].append(item.get("week_key"))
        output["dates"].append(item.get("publish_date"))
        output["Influenza"].append(item.get("influenza_pct"))
        output["RSV"].append(item.get("rsv_pct"))
        output["SARS-CoV-2"].append(item.get("sars_cov_pct"))
        output["Adenovirus"].append(item.get("adenovirus_pct"))
        output["Parainfluenza"].append(item.get("parainfluenza_pct"))
        output["Rhinovirus"].append(item.get("rhinovirus_pct"))
        output["hMPV"].append(item.get("hmpv_pct"))
    return output


@app.get("/influenza/")
async def influenza_trend():
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
        modules={'models': ['wpdb.models']}
    )
    data_2019_2020 = await MultiPathogen.filter(season="2019-2020").values()
    data_2020_2021 = await MultiPathogen.filter(season="2020-2021").values()
    data_2021_2022 = await MultiPathogen.filter(season="2021-2022").values()
    output = {
        "week": [],
        "influenza_2019_2020": [],
        "influenza_2020_2021": [],
        "influenza_2021_2022": [],
    }
    for item in data_2019_2020:
        output["week"].append(item.get("week"))
        output["influenza_2019_2020"].append(item.get("influenza_pct"))

    for i in data_2020_2021:
        output["influenza_2020_2021"].append(i.get("influenza_pct"))

    for i in data_2021_2022:
        output["influenza_2021_2022"].append(i.get("influenza_pct"))

    return output


@app.post("/reset/")
async def delete_record():
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
        modules={'models': ['wpdb.models']}
    )
    saved_items = await MultiPathogen.all().delete()
    return {}


@app.post("/import/")
async def import_file():
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
        modules={'models': ['wpdb.models']}
    )
    s3 = boto3.client('s3')
    object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=FILENAME)
    data = object['Body'].read().decode('utf-8')
    data_lines = data.splitlines()
    return data_lines
    #lines = csv.DictReader(data_lines)
    #for line in lines:
    #    logger.info(line)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    #try:
    contents = file.file.read().decode('utf-8')
    lines = contents.splitlines()
    for line in lines:
        logging.info(line)
        items = ",".split(line)
        if items[0] != "Week" and len(items) == 16:
            await create_new_record(items)

    #except Exception:
    #    return {"message": "There was an error uploading the file"}
    #finally:
    file.file.close()

    return {"message": f"{len(lines)-1} records processed"}


async def create_new_record(items: list):
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
        modules={'models': ['wpdb.models']}
    )
    multipathogen = await MultiPathogen.create(
        week=items[0],
        year=items[1],
        week_key=items[2],
        publish_date=items[3],
        season=items[4],
        influenza_pct=items[5],
        rsv_pct=items[6],
        rhinovirus_pct=items[7],
        parainfluenza_pct=items[8],
        hmpv_pct=items[9],
        adenovirus_pct=items[10],
        sars_cov_pct=items[11],
        influenza_a_h3n2_n_pct=items[12],
        influenza_a_h1n1_pdm09_n_pct=items[13],
        influenza_a_not_subtyped_n_pct=items[14],
        influenza_b_n_pct=items[15]
    )
    result = await multipathogen.save()
    logging.info(result)

@app.post("/items/")
async def create_record(record: Record):
    await Tortoise.init(
        config=settings.TORTOISE_ORM,
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
    logging.info(result)
    return result


@app.get("/testdata/")
async def test_data():
    file_path = os.path.join(settings.BASE_DIR, 'tests',
                             'fixtures', 'multi_pathogen.csv')

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

    run(app, port=80)
