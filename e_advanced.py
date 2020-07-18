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










# Custom Request
# Use this to prepare requests' body: msgpack, gzip, etc

import gzip
from typing import Callable, List

from fastapi import Body, FastAPI, Request, Response
from fastapi.routing import APIRoute

class GzipRequest(Request):
    """ Custom request that un-gzips itself """
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = gzip.decompress(body)
            self._body = body
        return self._body


class GzipRoute(APIRoute):
    """ Custom route """
    # Returns a callable.
    # Basically, acts like a middleware
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = GzipRequest(
                # ASGI spec
                request.scope,  # request metadata
                request.receive  # a function to "receive" the body of the request.
            )

            # Call the parent route handler
            # NOTE: try..except block can be used to catch exceptions , e.g. validation errors
            # You can also use it for timing requests
            return await original_route_handler(request)

        return custom_route_handler


app = FastAPI()
app.router.route_class = GzipRoute  # use our custom classes







# Validation error logging
# We'll use APIRoute's handler as a middleware

from fastapi.exceptions import HTTPException, RequestValidationError


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                # Call the route, and, the operation
                return await original_route_handler(request)
            except RequestValidationError as exc:
                # Process validation errors
                body = await request.body()
                detail = {"errors": exc.errors(), "body": body.decode()}

                # Make an exception
                raise HTTPException(status_code=422, detail=detail)

        return custom_route_handler


app = FastAPI()
app.router.route_class = ValidationErrorLoggingRoute


