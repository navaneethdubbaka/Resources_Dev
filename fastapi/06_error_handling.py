"""Return an intentional HTTP error when a requested resource is absent."""

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Error Handling")

BOOKS = {1: "Python for Beginners", 2: "HTTP in Practice"}


@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict[str, int | str]:
    title = BOOKS.get(book_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"book_id": book_id, "title": title}
