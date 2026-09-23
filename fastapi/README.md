# `fastapi`: Building APIs with Python

Phase 1 used `requests` as a **client** to call APIs. This module reverses the perspective: FastAPI is a Python framework that creates a **server** API other programs can call.

```text
Client
  -> HTTP request
FastAPI application
  -> route -> validation -> application logic -> JSON response
Client
```

## Core ideas

- **Why APIs exist:** they give programs a stable, documented interface to exchange data and actions.
- **FastAPI:** a Python framework for defining HTTP endpoints with ordinary Python functions and type hints.
- **ASGI:** a standard interface between an asynchronous Python web server (such as Uvicorn) and an application (such as FastAPI). At this level, remember: Uvicorn runs FastAPI and passes HTTP requests to it.
- **Application object:** `app = FastAPI()` is the application being served.
- **Route:** a pairing of an HTTP method and path with a Python function, such as `@app.get("/")`.
- **Response JSON:** returning a dictionary makes FastAPI serialize it as JSON.
- **Swagger/OpenAPI:** FastAPI generates an interactive API page at `/docs` and a machine-readable API description at `/openapi.json`.

## Setup and running an example

Dependencies are pinned in `requirements.txt`. Install them from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start one app at a time (use a different port only if `8000` is already busy):

```powershell
.\.venv\Scripts\python.exe -m uvicorn 01_hello_api:app --app-dir fastapi --reload
```

Then open `http://127.0.0.1:8000/docs` or make the documented request. Stop the server with `Ctrl+C`. See [08_project_structure.md](08_project_structure.md) for why the module uses separate small apps.

## Example 1 — Hello API (`01_hello_api.py`)

### 1. What are we trying to build?

An API endpoint that returns a welcome message.

### 2. Why do we need it?

It makes the client/server direction concrete before introducing inputs.

### 3. Architecture

```text
GET / -> FastAPI route -> home() -> JSON response
```

### 4. Before code

The decorator connects a request method/path to a Python function.

### 5. Code

See `01_hello_api.py`.

### 6. Important lines

`FastAPI()` creates the app; `@app.get("/")` registers a GET route; the returned dictionary becomes JSON.

### 7. Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn 01_hello_api:app --app-dir fastapi
```

Then request `GET http://127.0.0.1:8000/`.

### 8. Expected output

`{"message":"Hello AI Engineering"}` with HTTP `200`.

### 9. What changed?

Unlike `requests`, this code waits for another program to call it.

### 10. Experiment

Change the welcome message.

### 11. Common errors

`Error loading ASGI app` usually means the module name, `app` name, or `--app-dir` is wrong.

### 12. Connection

Paths can contain values that identify a specific resource.

## Example 2 — Path parameters (`02_path_parameters.py`)

### 1. What are we trying to build?

Routes that read `/users/123` and `/products/10`.

### 2. Why do we need it?

Path parameters identify a particular resource.

### 3. Architecture

```text
GET /users/123 -> user_id=123 -> get_user() -> JSON
```

### 4. Before code

The name inside `{user_id}` must match the function parameter. The `int` type asks FastAPI to parse and validate it.

### 5. Code

See `02_path_parameters.py`.

### 6. Important lines

`/users/{user_id}` declares a placeholder; `user_id: int` converts a valid URL value to an integer.

### 7. Run

Start `02_path_parameters:app` with `--app-dir fastapi`, then request `/users/123` and `/products/10`.

### 8. Expected output

`/users/123` returns `{"user_id":123,"message":"User 123"}`.

### 9. What changed?

The route function now receives input from the URL path.

### 10. Experiment

Request `/users/not-a-number` and inspect the validation response.

### 11. Common errors

A non-integer value returns `422 Unprocessable Entity`; that is automatic validation, not a server crash.

### 12. Connection

Query parameters supply filtering or options without identifying a new path resource.

## Example 3 — Query parameters (`03_query_parameters.py`)

### 1. What are we trying to build?

A `/search?query=python&limit=3` endpoint.

### 2. Why do we need it?

Queries express options such as search terms, pagination, and filters.

### 3. Architecture

```text
GET /search?query=python -> query, limit -> search() -> JSON
```

### 4. Before code

Everything after `?` is a query string. Unlike `/users/123`, it does not form part of the path identity.

### 5. Code

See `03_query_parameters.py`.

### 6. Important lines

`query: str` is required; `limit: int = 5` is optional and defaults to five.

### 7. Run

Start `03_query_parameters:app`, then request `GET /search?query=python&limit=3`.

### 8. Expected output

The returned JSON repeats `query: "python"` and `limit: 3`.

### 9. What changed?

Input now comes after `?`, rather than inside the path.

### 10. Experiment

Omit `limit` and observe its default.

### 11. Common errors

Omitting required `query` produces a 422 validation response.

### 12. Connection

For larger data, clients send a JSON request body with POST.

## Example 4 — POST request (`04_post_request.py`)

### 1. What are we trying to build?

An endpoint that receives and echoes a JSON body.

### 2. Why do we need it?

Clients often send data that does not fit naturally in a URL.

### 3. Architecture

```text
POST /messages + JSON body -> payload -> create_message() -> JSON
```

### 4. Before code

The client sends `Content-Type: application/json`; FastAPI parses the body before calling the function.

### 5. Code

See `04_post_request.py`.

### 6. Important lines

`payload: dict[str, Any] = Body()` declares that `payload` comes from the JSON request body.

### 7. Run

Start `04_post_request:app`, then POST `{"text":"Hello"}` to `/messages`.

### 8. Expected output

HTTP `200` and `{"received":{"text":"Hello"},"message":"JSON body received"}`.

### 9. What changed?

The client sends structured data to the API.

### 10. Experiment

Send two fields and inspect the echoed object.

### 11. Common errors

Invalid JSON yields a validation response. Set `json=` when calling with Python `requests`.

### 12. Connection

Unstructured dictionaries are flexible; Pydantic makes expected data predictable.

## Example 5 — Pydantic models (`05_pydantic_models.py`)

### 1. What are we trying to build?

Create a user only when `name` and a sensible integer `age` are provided.

### 2. Why do we need it?

Applications need reliable input before business logic uses it.

### 3. Architecture

```text
POST JSON -> User schema -> validation -> create_user() -> JSON or 422
```

### 4. Before code

Pydantic models use type hints and constraints to describe a request schema. FastAPI uses that schema automatically.

### 5. Code

See `05_pydantic_models.py`.

### 6. Important lines

`BaseModel` defines the schema; `Field(ge=0, le=130)` constrains age; `status_code=201` communicates creation.

### 7. Run

Start `05_pydantic_models:app`, then POST `{"name":"Ada","age":25}` to `/users`.

### 8. Expected output

HTTP `201` and the created user fields. Sending `{"name":"","age":-1}` returns HTTP `422` with validation details.

### 9. What changed?

The API now declares and enforces its expected body shape.

### 10. Experiment

Add an `email` field to `User` and test a valid request.

### 11. Common errors

`422` means the client input did not match the declared schema. It is useful feedback, not an unhandled exception.

### 12. Connection

Validation handles bad input; applications also need intentional errors for missing resources.

## Example 6 — Error handling (`06_error_handling.py`)

### 1. What are we trying to build?

Return a clear 404 JSON error for a book that is not in a small local collection.

### 2. Why do we need it?

Not every valid-looking request can succeed; clients need a meaningful status and message.

### 3. Architecture

```text
GET /books/99 -> lookup -> absent -> HTTPException(404) -> error JSON
```

### 4. Before code

Use `HTTPException` for expected HTTP-level failures, rather than returning an accidental `200` with a vague string.

### 5. Code

See `06_error_handling.py`.

### 6. Important lines

`BOOKS.get` avoids a `KeyError`; `raise HTTPException(...)` stops the route and constructs an HTTP error response.

### 7. Run

Start `06_error_handling:app`, then request `/books/1` and `/books/99`.

### 8. Expected output

`/books/1` is `200`; `/books/99` is `404` with `{"detail":"Book not found"}`.

### 9. What changed?

The route now distinguishes success from a known missing-resource failure.

### 10. Experiment

Add one more book to `BOOKS`.

### 11. Common errors

Do not expose secrets or internal stack traces in an error `detail`.

### 12. Connection

The final example combines request validation and a downstream LLM service.

## Example 7 — FastAPI + LLM (`07_llm_endpoint.py`)

### 1. What are we trying to build?

A `POST /chat` API endpoint that validates a message, calls an OpenAI-compatible provider, and returns an answer.

### 2. Why do we need it?

FastAPI becomes the application interface; the LLM is one component behind it.

### 3. Architecture

```text
client -> POST /chat -> ChatRequest validation -> LLM helper -> LLM API -> JSON answer
```

### 4. Before code

Set `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` in the shell before starting this server. They are documented in the root `.env.example`; never add the key to source.

### 5. Code

See `07_llm_endpoint.py`.

### 6. Important lines

`ChatRequest` prevents empty messages; `get_llm_config` validates environment setup; `503` signals unavailable server configuration and `502` signals provider failure.

### 7. Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn 07_llm_endpoint:app --app-dir fastapi
```

POST `{"message":"Explain JSON briefly."}` to `/chat`.

### 8. Expected output

With valid credentials, HTTP `200` and `{"answer":"..."}`. The generated wording is non-deterministic.

### 9. What changed?

The LLM call from Phase 1 is now hidden behind an API other clients can use.

### 10. Experiment

Return the original message alongside `answer`.

### 11. Common errors

Missing configuration returns `503`; invalid client input returns `422`; invalid provider credentials commonly become a provider failure represented here as `502`.

### 12. Connection

Calling a model directly works, but larger applications need reusable prompt/model/parser components—LangChain’s next topic.

## Instructor Teaching Script

1. Ask: “Phase 1 called an API. What if another program needs to call our Python code?” Draw the client-to-FastAPI diagram.
2. Run Example 1, open `/docs`, and identify the app object, route, method, path, function, and JSON response.
3. Contrast `/users/123` with `/search?query=python`. Ask which one identifies a resource.
4. Send a POST body, then an invalid Pydantic body. Emphasize that schemas make input predictable before code runs.
5. Request a missing book and explain that useful APIs communicate failure intentionally.
6. Draw the LLM endpoint architecture. Ask students where credentials should live and why the frontend should call `/chat`, not expose the provider key.
7. Ask before proceeding: “If one LLM request needs a prompt, model, parser, and retrieval, how can we compose those pieces?” Expected answer: an orchestration framework such as LangChain.

## Student Exercises

1. Change the hello response.
2. Add a `/courses/{course_id}` path route.
3. Add a `page` query parameter to search.
4. Return a status code of `201` from the POST message example.
5. Add a constrained `email` field to `User` and test invalid data.

## Troubleshooting

| Symptom | Cause | Fix | Verification |
| --- | --- | --- | --- |
| `ModuleNotFoundError: fastapi` | Wrong interpreter or packages missing | Install with the project `.venv` interpreter | `python -c "import fastapi"` succeeds. |
| Uvicorn cannot import app | Incorrect module/path or app name | Use `--app-dir fastapi` and `:app` | Server logs “Application startup complete.” |
| Address already in use | Another process uses port 8000 | Stop it or add `--port 8001` | Browse the selected port. |
| `422` response | Path/query/body input violates a type/schema | Read the response `detail`, then correct the client input | A valid request returns 2xx. |
| `404` from an expected route | Incorrect path or HTTP method | Check `/docs` | The documented route succeeds. |
| `/chat` returns `503` | LLM environment variables are missing | Set all three variables and restart Uvicorn | `/chat` proceeds to provider call. |
| `/chat` returns `502` | Provider/network/response problem | Check provider URL, key, model, and connectivity | Provider call succeeds with valid configuration. |

## Module boundary

This phase creates API servers only. It does not add LangChain, LangGraph, the dedicated test suite, shared utilities, or cross-module documentation; those remain in later phases.

## Student code-reading guide

Every file first creates `app = FastAPI(...)`; Uvicorn serves that object. In **01**, `@app.get("/")` maps a GET path to a dictionary JSON response. **02** names `{user_id}` and `{product_id}` path placeholders exactly like their typed function parameters. **03** uses typed function parameters as query inputs, with `limit=5` as a default. **04** marks a dictionary as `Body()` input so FastAPI parses POST JSON. **05** replaces the loose dictionary with a Pydantic `User` schema and field constraints; invalid input never reaches `create_user`. **06** looks up a local dictionary and raises `HTTPException(404, ...)` for a known missing resource. **07** validates a `ChatRequest`, reads LLM environment configuration, calls the provider through `requests`, and translates configuration/provider failures into safe HTTP `503`/`502` responses. Route decorators define the API contract; return values become JSON.
