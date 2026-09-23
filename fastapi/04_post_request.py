"""Accept a JSON request body with a POST route."""

from typing import Any

from fastapi import Body, FastAPI

app = FastAPI(title="POST Request")


@app.post("/messages")
def create_message(payload: dict[str, Any] = Body()) -> dict[str, Any]:
    return {"received": payload, "message": "JSON body received"}
