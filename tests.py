from fastapi import FastAPI
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
