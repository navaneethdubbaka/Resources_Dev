# FastAPI — Building HTTP APIs

> This module turns Python from an API client into an API server: define routes, receive URL and JSON input, validate data, return useful errors, and expose a configured LLM behind one endpoint.

The numbered Python files are intentionally independent FastAPI applications. Start one at a time, demonstrate it, stop it, then move to the next file.

## Learning objectives

- Create a FastAPI application and a GET route.
- Receive path and query parameters.
- Accept JSON request bodies with POST.
- Validate a predictable body with a Pydantic model.
- Return intentional HTTP errors with HTTPException.
- Build a thin LLM endpoint that hides provider configuration from API callers.

## Big picture

~~~mermaid
flowchart LR
    C[Client: browser, curl, or Python] -->|HTTP request| F[FastAPI route]
    F --> V[Parameter parsing<br/>and validation]
    V --> H[Route function]
    H -->|JSON response| C
    H -->|example 07| L[OpenAI-compatible LLM API]
    ENV[LLM environment variables] -. configures .-> L
~~~

## Before the code

| Term | Meaning in this module |
| --- | --- |
| FastAPI app | The Python object that receives HTTP requests. |
| Route / endpoint | A function associated with a method and URL, such as GET /. |
| Path parameter | A value embedded in a URL path, such as the 7 in /users/7. |
| Query parameter | A value after ?, such as limit=2 in /search?query=agents&limit=2. |
| Request body | Data sent with a request, commonly JSON in a POST. |
| Pydantic model | A typed schema FastAPI uses to validate body data. |
| Status code | The result of a request: 200 success, 201 created, 404 absent, 422 invalid input, etc. |
| Uvicorn | The ASGI server used to run these applications. |

> [!TIP]
> FastAPI uses type hints as part of its HTTP contract. A parameter annotated int is parsed and validated as an integer; a Pydantic model validates the JSON request body before the route function runs.

## Setup and running an application

The existing environment contains FastAPI, Uvicorn, and Pydantic. From the repository root, run exactly one numbered application:

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 01_hello_api:app --app-dir fastapi --reload
~~~

Then visit http://127.0.0.1:8000/ or call it from another terminal. The --app-dir fastapi option tells Uvicorn where the numbered module lives. Stop the server with Ctrl+C before starting another example.

> [!NOTE]
> Each file defines its own variable named app. They are not meant to run together as one application.

---

## 01 — Hello API

### What are we learning?

The smallest FastAPI application: construct FastAPI and register one GET route.

### Why do we need it?

Every API begins with an application object and a route that maps a request to Python code.

### Flow

~~~text
GET / → FastAPI app → home() → Python dictionary → JSON response
~~~

### Code

~~~python
"""The smallest FastAPI application: one GET route returning JSON."""

from fastapi import FastAPI

app = FastAPI(title="Hello API")


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Hello AI Engineering"}
~~~

### Important lines

- app = FastAPI(...) creates the application and gives its documentation a title.
- @app.get("/") maps HTTP GET requests at / to home().
- The return annotation describes a string-to-string dictionary.
- Returning a dictionary lets FastAPI serialize it as JSON.

### Execution flow

Uvicorn imports app. A client sends GET /, FastAPI calls home(), and the returned dictionary becomes a JSON response with status 200.

### Run

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 01_hello_api:app --app-dir fastapi --reload
~~~

### Expected output

Request:

~~~text
GET http://127.0.0.1:8000/
~~~

Response:

~~~json
{"message":"Hello AI Engineering"}
~~~

### What changed from the previous example?

This is the starting point.

### Try it yourself

Change the returned message, save the file, and refresh the endpoint while --reload is running.

---

## 02 — Path parameters

### What are we learning?

How to capture a resource identifier from the URL path and have FastAPI convert it to an integer.

### Why do we need it?

APIs often identify a specific resource in the path: one user, book, order, or product.

### Flow

~~~mermaid
flowchart LR
    A[GET /users/7] --> B[Match /users/{user_id}]
    B --> C[Convert user_id to int]
    C --> D[get_user(user_id)]
    D --> E[JSON response]
~~~

### Code

~~~python
"""Use URL path values to identify a particular resource."""

from fastapi import FastAPI

app = FastAPI(title="Path Parameters")


@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, int | str]:
    return {"user_id": user_id, "message": f"User {user_id}"}


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict[str, int | str]:
    return {"product_id": product_id, "message": f"Product {product_id}"}
~~~

### Important lines

- Braces in /users/{user_id} name a variable segment of the path.
- The function parameter has the same name, so FastAPI passes the captured value into it.
- : int requests integer parsing and validation.
- The second route repeats the pattern for a different resource.

### Execution flow

For GET /users/7, FastAPI matches the user route, converts 7 to int, calls get_user(7), and returns the dictionary as JSON. GET /products/3 uses the product route instead.

### Run

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 02_path_parameters:app --app-dir fastapi --reload
~~~

### Expected output

~~~text
GET /users/7     → {"user_id":7,"message":"User 7"}
GET /products/3  → {"product_id":3,"message":"Product 3"}
~~~

### What changed from the previous example?

Example 01 always returned the same response at /. This file makes the response depend on a value supplied in the path.

### Try it yourself

Request /users/42. Then request /users/not-a-number and inspect FastAPI’s validation response.

---

## 03 — Query parameters

### What are we learning?

How to receive filtering input from the query string, including a default value.

### Why do we need it?

Query parameters commonly control search, filtering, pagination, or sorting without changing the resource path.

### Flow

~~~text
GET /search?query=agents&limit=2
        ↓
search(query="agents", limit=2)
        ↓
JSON response
~~~

### Code

~~~python
"""Read optional filtering input from the query string."""

from fastapi import FastAPI

app = FastAPI(title="Query Parameters")


@app.get("/search")
def search(query: str, limit: int = 5) -> dict[str, int | str]:
    return {"query": query, "limit": limit, "message": f"Searching for {query}"}
~~~

### Important lines

- query has no default, so it is required.
- limit: int = 5 is optional and defaults to 5.
- FastAPI converts limit from URL text to an integer.

### Execution flow

FastAPI reads values after ?. A search request with both values calls search() with those values. If limit is omitted, the function receives 5.

### Run

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 03_query_parameters:app --app-dir fastapi --reload
~~~

### Expected output

~~~text
GET /search?query=agents&limit=2 → {"query":"agents","limit":2,"message":"Searching for agents"}
GET /search?query=agents         → {"query":"agents","limit":5,"message":"Searching for agents"}
~~~

### What changed from the previous example?

Path parameters identify a resource as part of the route. This example supplies optional controls after ? on a fixed /search route.

### Try it yourself

Omit query. What status code and validation detail does FastAPI return?

---

## 04 — Accept a POST JSON body

### What are we learning?

How to receive an unstructured JSON object in a POST endpoint.

### Why do we need it?

When a client needs to send data rather than encode it in a URL, it normally uses a request body.

### Flow

~~~mermaid
sequenceDiagram
    participant C as Client
    participant A as POST /messages
    C->>A: JSON request body
    A->>A: payload dictionary
    A-->>C: received payload + confirmation
~~~

### Code

~~~python
"""Accept a JSON request body with a POST route."""

from typing import Any

from fastapi import Body, FastAPI

app = FastAPI(title="POST Request")


@app.post("/messages")
def create_message(payload: dict[str, Any] = Body()) -> dict[str, Any]:
    return {"received": payload, "message": "JSON body received"}
~~~

### Important lines

- @app.post registers a POST route.
- Body() marks payload as data from the JSON request body.
- dict[str, Any] accepts a JSON object with arbitrary keys and value types.
- The response echoes the received body for demonstration.

### Execution flow

A client POSTs a JSON object. FastAPI parses it into payload, calls create_message(), and serializes the returned dictionary as JSON.

### Run

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 04_post_request:app --app-dir fastapi --reload
~~~

In another PowerShell terminal:

~~~powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/messages -ContentType application/json -Body '{"topic":"HTTP"}'
~~~

### Expected output

~~~json
{"received":{"topic":"HTTP"},"message":"JSON body received"}
~~~

### What changed from the previous example?

Example 03 took small values from a URL. This route accepts a full JSON object in a POST body, but does not yet constrain its shape.

### Try it yourself

Send a body with two fields of different JSON types and inspect the echoed result.

---

## 05 — Validate a body with Pydantic

### What are we learning?

How a Pydantic model gives a JSON body a predictable shape and validation rules.

### Why do we need it?

The flexible dictionary in example 04 accepts any object. Real endpoints commonly require certain fields and valid ranges before business logic runs.

### Flow

~~~mermaid
flowchart LR
    C[POST JSON] --> V{User model validates?}
    V -->|yes| R[create_user]
    R --> S[201 JSON response]
    V -->|no| E[422 validation response]
~~~

### Code

~~~python
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
~~~

### Important lines

- User extends BaseModel, making it a request schema.
- name must be a non-empty string.
- age must be an integer from 0 through 130.
- user: User tells FastAPI to parse and validate the body before calling create_user().
- status_code=201 represents successful resource creation.

### Execution flow

For a valid JSON body, FastAPI creates User and calls create_user(). For invalid data, FastAPI does not call the function; it returns a 422 response describing the failed rules.

### Run

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 05_pydantic_models:app --app-dir fastapi --reload
~~~

Valid request:

~~~powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/users -ContentType application/json -Body '{"name":"Ada","age":37}'
~~~

### Expected output

Valid data returns status 201 and:

~~~json
{"message":"User created","name":"Ada","age":37}
~~~

An empty name or age below 0 returns 422 with validation details.

### What changed from the previous example?

Example 04 received any JSON object. This example requires a known shape and enforces constraints automatically.

### Try it yourself

POST name as an empty string and age as -1. Read the two validation errors returned by FastAPI.

---

## 06 — Return an intentional HTTP error

### What are we learning?

How an API chooses an HTTP error response when a requested resource does not exist.

### Why do we need it?

A missing resource should not look like a success, nor should it become an unhandled Python error. The client needs a clear status and explanation.

### Flow

~~~mermaid
flowchart TD
    A[GET /books/{book_id}] --> B[BOOKS.get(book_id)]
    B --> C{Title found?}
    C -->|Yes| D[200 + book JSON]
    C -->|No| E[HTTPException 404]
    E --> F[JSON detail: Book not found]
~~~

### Code

~~~python
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
~~~

### Important lines

- BOOKS is the small in-memory data source for this demonstration.
- .get() returns None when the ID is absent.
- Raising HTTPException stops normal route execution and sends the supplied status and detail.
- The normal return happens only for a known book.

### Execution flow

GET /books/1 finds a title and returns 200 JSON. GET /books/99 finds nothing and raises a 404 response with a useful detail field.

### Run

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn 06_error_handling:app --app-dir fastapi --reload
~~~

### Expected output

~~~text
GET /books/1  → 200 {"book_id":1,"title":"Python for Beginners"}
GET /books/99 → 404 {"detail":"Book not found"}
~~~

### What changed from the previous example?

Example 05 let FastAPI reject invalid input automatically with 422. This example’s input is valid, but the application itself determines that no requested book exists and explicitly returns 404.

### Try it yourself

Request /books/2, then /books/3. Explain why only the latter raises HTTPException.

---

## 07 — Expose an LLM behind POST /chat

### What are we learning?

How to combine a validated FastAPI endpoint with the requests-based OpenAI-compatible LLM client from the prior module.

### Why do we need it?

Clients can call one local API endpoint while server-side code protects provider configuration and translates provider failures into HTTP responses.

### Flow

~~~mermaid
sequenceDiagram
    participant C as API client
    participant F as FastAPI POST /chat
    participant E as Environment variables
    participant L as LLM provider
    C->>F: {"message":"Hello"}
    F->>F: validate ChatRequest
    E-->>F: endpoint, key, model
    F->>L: POST /chat/completions
    L-->>F: assistant content
    F-->>C: {"answer":"..."}
~~~

### Code

~~~python
"""Expose a configured OpenAI-compatible LLM call behind POST /chat."""

import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="LLM Chat API")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="The user's chat message")


def get_llm_config() -> tuple[str, str, str]:
    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "")
    if not all((base_url, api_key, model)):
        raise ValueError("LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL must be configured.")
    return base_url, api_key, model


def ask_llm(message: str) -> str:
    base_url, api_key, model = get_llm_config()
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": message}]},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"LLM provider request failed: {error}") from error


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    try:
        answer = ask_llm(request.message)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {"answer": answer}
~~~

### Important lines

- ChatRequest rejects an empty message before chat() runs.
- get_llm_config reads three required settings and never stores a key in source.
- ask_llm makes the provider call with a Bearer authorization header, JSON payload, and 30-second timeout.
- A missing local configuration becomes HTTP 503, meaning the service cannot currently fulfill the request.
- A provider or response-shape failure becomes HTTP 502, meaning an upstream service failed.

### Execution flow

FastAPI first validates the incoming message. chat() calls ask_llm(), which validates server configuration and calls the provider. A successful provider response is returned as answer. Missing configuration and provider failures are translated into API-friendly 503 and 502 responses.

### Run

Set valid provider-specific values in the terminal that will launch Uvicorn:

~~~powershell
$env:LLM_BASE_URL = "https://your-provider.example/v1"
$env:LLM_API_KEY = "your-secret-key"
$env:LLM_MODEL = "your-model-name"
.\.venv\Scripts\python.exe -m uvicorn 07_llm_endpoint:app --app-dir fastapi --reload
~~~

Then call it from another terminal:

~~~powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType application/json -Body '{"message":"Explain HTTP in one sentence."}'
~~~

### Expected output

With valid provider configuration, the response has this shape:

~~~json
{"answer":"...provider-generated answer..."}
~~~

With configuration absent, the existing code intentionally returns HTTP 503:

~~~json
{"detail":"LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL must be configured."}
~~~

### What changed from the previous example?

Example 06 returned a local 404. This example creates a real service boundary: it validates client input, calls an upstream HTTP API, and translates internal configuration or upstream failures into public HTTP responses.

### Try it yourself

POST an empty message. Explain why FastAPI returns 422 before attempting any LLM request.

---

## 08 — Project structure

The supplied [08_project_structure.md](08_project_structure.md) explains the teaching layout: every numbered Python file is an independent application. The current folder is:

~~~text
fastapi/
├── 01_hello_api.py          # one GET route
├── 02_path_parameters.py    # values inside a URL path
├── 03_query_parameters.py   # values after ? in a URL
├── 04_post_request.py       # unstructured JSON body
├── 05_pydantic_models.py    # validated JSON body
├── 06_error_handling.py     # intentional 404 response
├── 07_llm_endpoint.py       # credential-safe LLM bridge
└── 08_project_structure.md
~~~

Run one application at a time with its own module name and --app-dir fastapi. This preserves the small, focused live demonstrations; there is intentionally no shared folder in this phase.

---

## Learning progression

~~~mermaid
flowchart LR
    A[01<br/>GET route] --> B[02<br/>Path parameters]
    B --> C[03<br/>Query parameters]
    C --> D[04<br/>POST JSON]
    D --> E[05<br/>Pydantic validation]
    E --> F[06<br/>Intentional errors]
    F --> G[07<br/>LLM endpoint]
    G --> H[08<br/>Independent app structure]
~~~

| File | Concept | Why it comes next |
| --- | --- | --- |
| 01_hello_api.py | First route | Establishes app, decorator, JSON response. |
| 02_path_parameters.py | Resource IDs | Makes URL paths dynamic. |
| 03_query_parameters.py | Filtering input | Adds optional URL controls and defaults. |
| 04_post_request.py | JSON body | Moves richer client data out of the URL. |
| 05_pydantic_models.py | Validation | Makes body requirements explicit and automatic. |
| 06_error_handling.py | 404 response | Handles a valid request whose resource is absent. |
| 07_llm_endpoint.py | Upstream LLM bridge | Combines validation, HTTP clients, secrets, and error translation. |
| 08_project_structure.md | Teaching layout | Explains why each application stays independent. |

## Code → concept

| File | HTTP surface | What it teaches |
| --- | --- | --- |
| 01_hello_api.py | GET / | Return JSON from the smallest FastAPI app. |
| 02_path_parameters.py | GET /users/{id}, /products/{id} | Capture and type URL path values. |
| 03_query_parameters.py | GET /search | Required and default query parameters. |
| 04_post_request.py | POST /messages | Receive an unstructured JSON object. |
| 05_pydantic_models.py | POST /users | Validate required fields and return 201. |
| 06_error_handling.py | GET /books/{id} | Return 200 or intentional 404. |
| 07_llm_endpoint.py | POST /chat | Validate input and proxy a configured LLM call. |

## Common errors

<details>
<summary><strong>Uvicorn cannot import the module</strong></summary>

~~~text
Problem: Uvicorn reports it cannot import 01_hello_api or another numbered module
↓
Why it happens: the command was not started from the repository root, or Uvicorn was not told that modules are in fastapi/
↓
How to fix: use --app-dir fastapi, for example:
            .\.venv\Scripts\python.exe -m uvicorn 01_hello_api:app --app-dir fastapi --reload
~~~
</details>

<details>
<summary><strong>Address already in use</strong></summary>

~~~text
Problem: Uvicorn cannot bind its default local port
↓
Why it happens: another server is still running on port 8000
↓
How to fix: stop the prior server with Ctrl+C, or run with --port followed by an unused port
~~~
</details>

<details>
<summary><strong>422 Unprocessable Entity</strong></summary>

~~~text
Problem: FastAPI returns 422
↓
Why it happens: route input did not match the declared type/schema—such as missing query, non-integer path value, empty name, or age outside 0–130
↓
How to fix: read the JSON detail response, then send data matching the route signature or Pydantic model
~~~
</details>

<details>
<summary><strong>404 Book not found</strong></summary>

~~~text
Problem: GET /books/99 returns 404
↓
Why it happens: the example only contains book IDs 1 and 2
↓
How to fix: no change is needed for the demo; request /books/1 or /books/2 to follow the success path
~~~
</details>

<details>
<summary><strong>503 from POST /chat</strong></summary>

~~~text
Problem: the endpoint says LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL must be configured
↓
Why it happens: the server process has not received all three environment variables
↓
How to fix: set valid provider-specific values in the same terminal before starting Uvicorn; never add them to source code
~~~
</details>

<details>
<summary><strong>502 from POST /chat</strong></summary>

~~~text
Problem: FastAPI reports an LLM provider request failed error
↓
Why it happens: the upstream key, URL, model, network connection, or response format is invalid
↓
How to fix: check the provider’s OpenAI-compatible endpoint, authentication, model name, and availability
~~~
</details>

## Instructor teaching flow

~~~text
START
 ↓
Bridge from requests: “We called APIs; now Python will build one.”
 ↓
Explain client, server, route, request, and response
 ↓
Start 01 and call GET /
 ↓
Ask students where the URL and returned JSON are declared
 ↓
Use 02 and 03 to compare path values with query values
 ↓
Use 04 to move data from URL into a POST body
 ↓
Use 05 to show automatic validation and the 422 path
 ↓
Use 06 to distinguish invalid input from a missing resource
 ↓
Use 07 to trace client → FastAPI → LLM provider → client
 ↓
Explain environment-variable safety and 503 versus 502
 ↓
Review 08: one application at a time
~~~

Useful questions:

- What does the decorator tell FastAPI?
- Why is user_id: int more useful than accepting arbitrary text?
- When would you put data in a path, query string, or JSON body?
- Why does example 05 return 422 without entering create_user()?
- How is the 404 in example 06 different from 422?
- Why should the LLM key exist on the server but not in a browser client?
- What does FastAPI add around the requests call in example 07?

## Student exercises

~~~text
Easy → Small modification → Concept combination
~~~

1. **Easy:** Change example 01’s greeting and see --reload apply it.
2. **Small modification:** Add a GET /teams/{team_id} route to example 02 using the same path-parameter pattern.
3. **Small modification:** Add a default query parameter to example 03 and return it in the response.
4. **Small modification:** POST two different fields to example 04 and observe the echo.
5. **Concept combination:** Add one field with a validation rule to User in example 05, then test valid and invalid bodies.
6. **Concept combination:** Add one item to BOOKS and verify its success response versus an absent ID’s 404.
7. **LLM extension:** With valid LLM configuration, change the submitted message. Explain which parts stay inside the server boundary.

## Key takeaways

- A FastAPI route connects an HTTP method and URL to a Python function.
- Type hints define and validate path and query input.
- POST bodies carry JSON data; Pydantic models make that data predictable.
- 422 signals invalid input; 404 signals an absent resource.
- An API can translate upstream configuration and provider errors into meaningful HTTP responses.
- Independent, small applications are useful for focused demonstrations.

## Connection to the next module

~~~mermaid
flowchart LR
    A[requests] --> B[“I can CALL an API.”]
    B --> C[FastAPI]
    C --> D[“I can BUILD an API.”]
    D --> E[LangChain]
    E --> F[“I can compose LLM-powered workflows.”]
~~~

FastAPI exposes the interface. The next module, langchain/, will focus on composing LLM calls and higher-level chains behind or alongside that interface.
