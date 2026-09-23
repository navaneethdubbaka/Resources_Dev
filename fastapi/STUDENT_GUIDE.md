# FastAPI: slow student walkthrough

Uvicorn is the server process. It imports `app`, waits for HTTP requests, then FastAPI matches each request to a decorated function. A returned Python dictionary becomes JSON automatically.

## 01 — Hello

`FastAPI(...)` creates the application object. `@app.get("/")` registers the function below it: GET requests to `/` call `home`. The annotation describes a dictionary of strings. Calling the route returns a dictionary, and FastAPI serializes it to JSON with status 200.

## 02 — Path parameters

`/users/{user_id}` contains a variable URL segment. The placeholder name and function parameter must match. `user_id: int` means FastAPI converts text like `123` to an integer before calling the function; non-numeric text returns 422 instead of crashing. The product route repeats the same pattern for comparison.

## 03 — Query parameters

`/search?query=python&limit=3` leaves the path as `/search` and supplies options after `?`. `query: str` has no default, so it is required. `limit: int = 5` is optional and is converted from URL text to an integer. The response echoes what FastAPI parsed.

## 04 — POST body

`@app.post` registers a POST route. `payload: dict[str, Any] = Body()` tells FastAPI that JSON body data should become a Python dictionary. `Any` makes this deliberately flexible; it proves body parsing but does not guarantee a useful shape. The next example fixes that limitation.

## 05 — Pydantic validation

`User(BaseModel)` is a request schema. `name` must be nonempty; `age` must be an integer from 0 to 130. FastAPI parses JSON into `User` before `create_user` executes. Invalid data receives structured HTTP 422 details. `status_code=201` communicates a new resource was created.

## 06 — Expected errors

`BOOKS` is a tiny in-memory data store. `.get` returns `None` if a key is absent. Rather than returning fake success, `HTTPException(404, ...)` stops the route and creates `{ "detail": "Book not found" }`. A 404 is a meaningful result for a missing resource.

## 07 — LLM endpoint

`ChatRequest` rejects blank messages. `get_llm_config` checks environment variables; missing server setup becomes HTTP 503. `ask_llm` makes the provider request and extracts answer text; provider/network/response problems become 502. The route exposes only `/chat` and an answer, keeping provider keys on the backend.
