from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, TypeVar, Generic
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    # App title, used in docs
    title='simplest'
)

# uvicorn simplest:app --reload

# OpenAPI docs: http://127.0.0.1:8000/docs
# ReDoc:        http://127.0.0.1:8000/redoc
# OpenAPI JSON: http://127.0.0.1:8000/openapi.json

# Operations:
# POST: to create data.
# GET: to read data.
# PUT: to update data.
# DELETE: to delete data.

# http://127.0.0.1:8000/
@app.get("/")
async def read_root():
    # You can return:
    # dict, list, singular values as str, int, etc.
    # Pydantic models
    # many other objects and models
    # ORM models
    return {"Hello": "World"}


# http://127.0.0.1:8000/items/5?q=somequery
# One path parameter, one query parameter
@app.get("/items/{item_id}")
def read_item_by_id(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


# Using enums
class ItemType(str, Enum):
    ALEXNET = "alexnet"
    RESNET = "resnet"
    LENET = "lenet"

@app.get("/item_type/{item_type}")
def read_item_by_type(item_type: ItemType):
    # Enum will be converted to its **value** (not name)
    return {"item_type": item_type}

# Using paths
@app.get("/item_path/{path:path}")
def read_item_by_type(path: str):
    return {'path': path}


# Interface: data model
class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None
    when: Optional[datetime]


# Saving: body as JSON (`item`)
# singular parameters (like int, float, str, bool, etc) are interpreted as query parameters
# Pydantic models are interpreted as a request body.
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


