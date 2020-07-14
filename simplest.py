from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# uvicorn simplest:app --reload

# OpenAPI docs: http://127.0.0.1:8000/docs
# ReDoc:        http://127.0.0.1:8000/redoc


# http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return {"Hello": "World"}


# http://127.0.0.1:8000/items/5?q=somequery
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


# Interface: data model
class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None
    when: Optional[datetime]


# Saving: body as JSON (`item`)
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


