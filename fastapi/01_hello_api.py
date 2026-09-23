"""The smallest FastAPI application: one GET route returning JSON."""

from fastapi import FastAPI

app = FastAPI(title="Hello API")


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Hello AI Engineering"}
