from __future__ import annotations
import time
from datetime import datetime
from enum import Enum
from random import randint
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, Field, HttpUrl
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi import Query, Path, Body, Cookie, Header, Form, File, UploadFile

app = FastAPI(
    # App title and version, used in docs
    title='simplest',
    version='0.0.1',
)

# Running:
# uvicorn a_intro:app --reload

# OpenAPI docs: http://127.0.0.1:8000/docs
# ReDoc:        http://127.0.0.1:8000/redoc
# OpenAPI JSON: http://127.0.0.1:8000/openapi.json

# Operations:
# POST: to create data.
# GET: to read data.
# PUT: to update data (whole or partial).
# DELETE: to delete data.
# PATCH: for partial updates (some teams use it)






# http://127.0.0.1:8000/
@app.get("/", status_code=200)
# When you use the async methods, FastAPI runs the file methods in a threadpool and awaits for them.
async def read_root(
        response: Response,
        user_agent: str = Header(None),  # takent from headers
        user_id: int = Cookie(None),  # taken from a cookie
    ):
    response.set_cookie('user_id', randint(0,999))
    # You can return:
    # dict, list, singular values as str, int, etc.
    # Pydantic models
    # many other objects and models
    # ORM models
    return {"Hello": "World",
            'user_id': user_id,
            'User-Agent': user_agent,
            }









# Using enums
class ItemType(str, Enum):
    ALEXNET = "alexnet"
    RESNET = "resnet"
    LENET = "lenet"


# http://127.0.0.1:8000/items/5?q=somequery
# One path parameter, one query parameter
@app.get("/items/{item_id}",
         # 'tags' used for OpenAPI docs navigation as categories
         tags=['items'],
         # Describe the API (OpenAPI docs)
         summary='API summary (right next to the title)',
         response_description='Description for the response value',
         # Deprecate an API (OpenAPI docs)
         deprecated=True,
         )
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
    """ Provide API description **as Markdown** """
    # Enums will be converted to their **values** (not names)
    return {"item_id": item_id, "q": q, 'item_type': item_type}






# Using paths
@app.get("/item_path/{path:path}")
def read_item_by_type(path: str):
    return {'path': path}








# Interface: data model, saving objects
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


class PutItemResponse(BaseModel):
    item_name: str
    item_id: int
    with_default_value: int = 0

# Saving: body as JSON (`item`)
@app.put("/items/{item_id}",
         status_code=status.HTTP_201_CREATED,  # created
         # Response model
         response_model=PutItemResponse,
         # Remove default values; only use those explicitly set
         response_model_exclude_unset=True,
         # Remove None values
         response_model_exclude_none=True,
         # Include/exclude individual fields (like the password field)
         # NOTE: it is recommended to use separate classes instead
         response_model_include=[],
         response_model_exclude=[],
         )
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}








# Partial updates
# NOTE: the input model is still validated! If you need to skip it, create a new model with all fields optional
@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    # Load
    db_item: Item = ...  # load it somehow and convert to a Pydantic type (from_orm())

    # Update the item using dict(exclude_unset=True) + copy(update)
    update_data = item.dict(exclude_unset=True)  # `exclude_unset`: omit defaults; only use values set by the user
    updated_item = db_item.copy(update=update_data)  # partial update

    # Save
    ...(jsonable_encoder(updated_item))

    # DOne
    return updated_item










# Saving from an HTML form
# OAUTH2 spec says those fields have to be named 'username' and 'password' and sent as form fields
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username, 'password': 'no way'}











# Example recursive models

# NOTE: in real world, you'll likely have multiple related models:
# * UserIn (input, with password)
# * UserOut (output, no password)
# * UserDB (DB model)
# * UserPart (partial user input)
# and do like this:
#   UserInDB(**user_in.dict(), hashed_password=hashed_password)
#
# But to reduce code duplication:
# use class inheritance ; Union[] ; generate partial classes

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















# Receiving files
@app.post("/files/")
async def create_file(
        # Stream of bytes
        # the whole contents will be stored in memory. For small files!
        file: bytes = File(...)):
    return {"file_size": len(file)}


# UploadFile
@app.post("/uploadfile/")
async def create_upload_file(
        # Uploaded file, partly on disk, with metadata available ("spooled" file)
        # It also has an async interface
        file: UploadFile = File(...)):
    return {"filename": file.filename,
            "contents": await file.read()
            }

# Upload many files at once
@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
        <body>
        <form action="/files/" enctype="multipart/form-data" method="post">
            <input name="files" type="file" multiple>
            <input type="submit">
        </form>
        <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
            <input name="files" type="file" multiple>
            <input type="submit">
        </form>
        </body>
    """
    return HTMLResponse(content=content)














# Report errors
@app.get("/item-by-id/{item_id}")
async def get_item_by_id(item_id: str):
    items = {"foo": "The Foo Wrestlers"}
    if item_id not in items:
        raise HTTPException(status_code=404,
                            # Will return a JSON response {'detail': {'msg': ...}}
                            detail={'msg': "Item not found"})
    return {"item": items[item_id]}

# Globally convert UnicornException to HTTPException
class UnicornException(Exception): pass

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


# Advanced: override the exception handler for validation errors
if False:
    from fastapi.encoders import jsonable_encoder

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            # exc.body: the body it received with invalid data.
            # jsonable_encoder() is what @vdmit11 calls "jsonify()" :)
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

        # you can reuse the default handler
        from fastapi.exception_handlers import request_validation_exception_handler
        request_validation_exception_handler(request, exc)

# Advanced: override the exception handler for HTTP errros
if False:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)






# Middleware
# Wraps path operations
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Measure execution time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add header
    response.headers["X-Process-Time"] = str(process_time)
    return response








# CORS
# Cross-origin: when the UI runs on a host different from the API
# Origin: scheme+domain+port

# Then, the browser will send an HTTP OPTIONS request to the backend, and if the backend sends
# the appropriate headers authorizing the communication from this different origin,
# then the browser will let the JavaScript in the frontend send its request to the backend.
#
# To achieve this, the backend must have a list of "allowed origins".

# It's also possible to declare the list as "*" (a "wildcard") to say that all are allowed.
# But that will only allow certain types of communication, excluding everything that
# involves credentials: Cookies, Authorization headers like those used with Bearer Tokens, etc.
#
# So, for everything to work correctly, it's better to specify explicitly the allowed origins.

# You can configure it in your FastAPI application using the CORSMiddleware.
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    # Origins permitted to make cross-origin requests
    allow_origins=origins,  # as a list
    allow_origin_regex=None,  # as a regexp
    # Allowed
    allow_credentials=True,  # Credentials (Authorization headers, Cookies, etc).
    allow_methods=["*"],  # HTTP methods
    allow_headers=["*"],  # HTTP headers
    # List of response HTTP headers that should be made accessible to the browser
    expose_headers=[],
)


