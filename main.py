from fastapi import FastAPI
from pydantic import BaseModel



class Item(BaseModel):
    title: str
    description: str | None = None
    price: float
    year: int | None = None

app = FastAPI()


@app.post("/items/{item_id}")
async def root(item_id: str, item: Item):
    if item.year == 2024:
        item.price *= 0.9
        name = item.title + ": " + item.description + " (discounted)"
    else:
        name = item.title + ": " + item.description
    return name