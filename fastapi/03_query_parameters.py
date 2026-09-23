"""Read optional filtering input from the query string."""

from fastapi import FastAPI

app = FastAPI(title="Query Parameters")


@app.get("/search")
def search(query: str, limit: int = 5) -> dict[str, int | str]:
    return {"query": query, "limit": limit, "message": f"Searching for {query}"}
