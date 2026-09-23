"""Use a Pydantic model to validate a predictable request body."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Pydantic Models")


class User(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=130)


@app.post("/users", status_code=201)
def create_user(user: User) -> dict[str, str | int]:
    return {"message": "User created", "name": user.name, "age": user.age}
