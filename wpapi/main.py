import csv
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tortoise import Tortoise, run_async
from typing import Union

import settings
from models import MultiPathogen


print("The app object is being created")
logging.debug("The app object is being created")


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


# This might not be needed as it's initiated in the 'start.sh' script
async def init(local=False):
    # await Tortoise.init(
    #     db_url='sqlite://db.sqlite3',
    #     modules={'models': ['wpdb.models']}
    # )
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


@app.get("/")
async def root():
    print("This is the root end point")
    logging.debug("This is the root end point")

    return {"message": "Hello World"}


@app.get("/items/")
async def read_item():
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


@app.put("/items/update/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_price": item.price, "item_id": item_id}


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
