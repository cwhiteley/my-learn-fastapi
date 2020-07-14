from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, Field, HttpUrl
from fastapi import FastAPI
from fastapi import Query, Path, Body

app = FastAPI(
    # App title and version, used in docs
    title='simplest',
    version='0.0.1',
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


# Using enums
class ItemType(str, Enum):
    ALEXNET = "alexnet"
    RESNET = "resnet"
    LENET = "lenet"


# http://127.0.0.1:8000/items/5?q=somequery
# One path parameter, one query parameter
@app.get("/items/{item_id}")
def read_item_by_id(
        # singular parameters (like int, float, str, bool, etc) are interpreted as query parameters
        # Pydantic models are interpreted as a request body.
        # Use Path(), Query(), Body() to mark parameters' source
        item_id: int = Path(..., # no default
                            title='Title for OpenAPI docs'
                            ),
        # query parameter
        q: Optional[str] = Query('fixedquery',  # default; use `...` for no default
                                 # validation
                                 min_length=3,
                                 max_length=60,
                                 regex="^fixedquery$"
                                 ),
        # This query parameter can be provided multiple times
        item_type: List[ItemType] = Query(
            [],
            title='Title for OpenAPI',
            description='Help text for OpenAPI',
            alias='itemType',  # another name, e.g. when not a valid Python identifier
            deprecated=True,  # stop using it
        )
        ):
    # Enums will be converted to their **values** (not names)
    return {"item_id": item_id, "q": q, 'item_type': item_type}


# Using paths
@app.get("/item_path/{path:path}")
def read_item_by_type(path: str):
    return {'path': path}


# Interface: data model
class Item(BaseModel):
    # Pydantic validation
    # (note: Query(), Path(), Body() are subclasses of Pydantic.field)
    name: str = Field(..., title='Name', description='Name', min_length=1)
    price: float
    is_offer: Optional[bool] = None
    when: Optional[datetime]
    image: Optional[Image]  # a forward reference!

    # Customize example
    class Config:
        schema_extra = {
            # Example: will go into the docs
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }

class Image(BaseModel):
    url: HttpUrl = Field(...,
                         # Docs info
                         title='Image URL',
                         example='http://example.com/example.png')
    name: str

Item.update_forward_refs()  # when forward references fail to update

# Saving: body as JSON (`item`)
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}





# Example recursive models

class User(BaseModel):
    id: int
    devices: List[Device]

class Device(BaseModel):
    uid: Optional[int]
    user: Optional[User]

User.update_forward_refs()
Device.update_forward_refs()

@app.put('/save')
def save(user: User):
    pass
