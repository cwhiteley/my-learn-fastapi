from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient

app = FastAPI()

# $ pip install pytest


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


client = TestClient(app)


# Test function: test_*()
def test_read_main():
    response = client.get("/")
    # Use normal assertions
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}







# Test websockets

@app.websocket_route("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()


def test_websocket():
    # Connect using `with`
    with client.websocket_connect("/ws") as websocket:
        # Receive
        data = websocket.receive_json()
        assert data == {"msg": "Hello WebSocket"}






# Test events

@app.on_event("startup")
async def startup_event():
    app.extra['startup'] = True


def test_read_items():
    with TestClient(app) as client:
        assert app.extra['startup'] == True
