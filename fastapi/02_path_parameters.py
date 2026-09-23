"""Use URL path values to identify a particular resource."""

from fastapi import FastAPI

app = FastAPI(title="Path Parameters")


@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, int | str]:
    return {"user_id": user_id, "message": f"User {user_id}"}


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict[str, int | str]:
    return {"product_id": product_id, "message": f"Product {product_id}"}
