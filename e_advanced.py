from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.responses import HTMLResponse

app = FastAPI(
    # a faster JSON encoder
    default_response_class=ORJSONResponse
)


# But if you return a Response directly, the data won't be automatically converted,
# and the documentation won't be automatically generated (for example, including the specific
# "media type", in the HTTP header Content-Type as part of the generated OpenAPI).


# JSON performance

# if you are squeezing performance, you can install and use orjson and set the response to be ORJSONResponse.
@app.get("/items/", response_class=ORJSONResponse)
async def read_items():
    return [{"item_id": "Foo"}]




# Serving by a proxy, with a prefix /api
# $ uvicorn main:app --root-path /api/v1
#   or
# app = FastAPI(root_path="/api/v1")





# Events

@app.on_event("startup")
async def startup_event():
    # Do things when the app initializes
    pass


@app.on_event("shutdown")
def shutdown_event():
    # Do things when the app is terminating
    pass
