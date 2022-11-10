from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel
from tortoise import Tortoise, run_async

from wpapi import settings
from wpapi.models import MultiPathogen

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
async def root():
    return {"message":"Hello World"}


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


@app.put("/items/update/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_price": item.price, "item_id": item_id}