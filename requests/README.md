# `requests`: Calling APIs from Python

This module teaches the first link in the Day 2 progression: **Python program -> HTTP request -> server -> HTTP response -> Python program**. `requests` is a client-side library: it calls an API. In the next module, FastAPI will let us build one.

## Core vocabulary

- **API (Application Programming Interface):** a documented interface through which one program asks another program for a service or data. APIs are not only for websites.
- **HTTP:** the request/response protocol commonly used by web APIs. A request has a method, URL, optional headers, and optional body; a response has a status code, headers, and body.
- **URL and endpoint:** a URL is an address; an endpoint is a specific API address and operation, such as `/todos/1`.
- **REST:** a common HTTP API style where URLs represent resources and HTTP methods express actions. It is a convention, not a Python library.
- **JSON:** a text data format made of objects, lists, strings, numbers, booleans, and `null`. `response.text` is raw text; `response.json()` parses JSON into Python data.
- **`requests`:** a Python package that creates HTTP requests and gives back response objects.

## HTTP building blocks

| Part | Meaning | Example |
| --- | --- | --- |
| GET | Ask a server for data | `GET /todos/1` |
| POST | Send data for the server to process/create | `POST /post` |
| Query parameter | Small input placed after `?` in a URL | `/search?topic=http` |
| Request body | Data sent with a request, often JSON | `{"name": "Ada"}` |
| Header | Metadata about a request | `Accept: application/json` |
| Status code | Result category | `200`, `404`, `401`, `429`, `500` |

Common status codes: `200 OK` means success; `201 Created` means a resource was created; `400 Bad Request` means input is invalid; `401 Unauthorized` usually means credentials are missing/invalid; `404 Not Found` means no matching endpoint/resource; `429 Too Many Requests` means rate limited; `500` means the server failed. Treat any response as fallible.

Headers commonly include `Accept` (response formats the client can read), `Content-Type` (the body format being sent), and `Authorization` (credentials). An API key is a secret used for authentication/authorization. Put it in an environment variable, never in source code or a committed `.env` file.

## Setup

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

All commands below use that same interpreter. The public examples need internet access. They use public teaching services, so their exact output can change. The LLM examples need credentials and are deliberately not run by default.

## Example 1 — GET request (`01_get_request.py`)

### 1. What are we trying to build?

A program that asks `https://example.com` for its page and prints the result status and text.

### 2. Why do we need it?

This establishes the simplest API conversation: a client asks, then a server answers.

### 3. Architecture

```text
Python -> requests.get() -> HTTP GET -> server -> response object
```

### 4. Before code

`requests.get(URL)` sends a GET request. The returned `response` holds the status and body.

### 5. Code

See `01_get_request.py`.

### 6. Important lines

`timeout=10` limits waiting; `raise_for_status()` turns an error status into an exception; `response.text` is decoded text.

### 7. Run

```powershell
.\.venv\Scripts\python.exe requests\01_get_request.py
```

### 8. Expected output

`Status code: 200`, followed by the opening of an HTML page.

### 9. What changed?

This is the baseline: no JSON body or custom headers yet.

### 10. Experiment

Change the URL to another public page and inspect its status code.

### 11. Common errors

`ConnectionError` means the network/DNS/proxy could not reach the host. `HTTPError` means the server returned an error status.

### 12. Connection

Many APIs return JSON, which is easier for programs to use than HTML.

## Example 2 — POST request (`02_post_request.py`)

### 1. What are we trying to build?

Send a JSON object to a service and read back what it received.

### 2. Why do we need it?

GET asks for data; POST sends data to the server. LLM prompts are commonly sent with POST.

### 3. Architecture

```text
Python -> POST + JSON body -> server -> JSON response -> Python dict
```

### 4. Before code

Passing `json=payload` makes `requests` serialize a Python dictionary as JSON and set the appropriate content type.

### 5. Code

See `02_post_request.py`.

### 6. Important lines

`payload` is the request body. `response.json()` parses the JSON response into a Python dictionary.

### 7. Run

```powershell
.\.venv\Scripts\python.exe requests\02_post_request.py
```

### 8. Expected output

The echoed JSON contains `name: Ada` and `topic: HTTP POST`.

### 9. What changed?

The client now supplies a request body rather than only a URL.

### 10. Experiment

Add a `course` field to `payload`.

### 11. Common errors

Do not use `data=` by accident when the API expects JSON; use the API documentation to choose the right format.

### 12. Connection

Headers tell the server additional information about this JSON request.

## Example 3 — Headers (`03_headers.py`)

### 1. What are we trying to build?

Make a request that includes metadata.

### 2. Why do we need it?

Servers need context such as accepted formats, client identity, and sometimes authorization.

### 3. Architecture

```text
Python -> URL + headers -> server -> response
```

### 4. Before code

Headers are not the response body. They describe how the client and server should communicate.

### 5. Code

See `03_headers.py`.

### 6. Important lines

`Accept` asks for JSON. `User-Agent` identifies this teaching client. A real `Authorization` value must come from an environment variable.

### 7. Run

```powershell
.\.venv\Scripts\python.exe requests\03_headers.py
```

### 8. Expected output

A dictionary of headers observed by the server, including the teaching `User-Agent`.

### 9. What changed?

The request now includes metadata in addition to the URL.

### 10. Experiment

Change the `User-Agent` value and find it in the response.

### 11. Common errors

Never paste a real `Authorization` key into this file, a screenshot, or a repository.

### 12. Connection

Next we parse a useful JSON response rather than only print raw text.

## Example 4 — JSON response (`04_json_request.py`)

### 1. What are we trying to build?

Fetch a JSON resource and read named fields from it.

### 2. Why do we need it?

JSON lets programs work with structured API data without manually splitting text.

### 3. Architecture

```text
GET -> JSON response text -> response.json() -> Python dictionary
```

### 4. Before code

Use `.json()` only when the server actually returns valid JSON. It is different from `.text`, which returns the raw body as text.

### 5. Code

See `04_json_request.py`.

### 6. Important lines

`data["title"]` accesses a dictionary value after JSON parsing.

### 7. Run

```powershell
.\.venv\Scripts\python.exe requests\04_json_request.py
```

### 8. Expected output

A todo object, its title, and a Boolean completion value.

### 9. What changed?

We convert a response body into Python data.

### 10. Experiment

Request `/todos/2` and compare the result.

### 11. Common errors

`JSONDecodeError` usually means the endpoint returned HTML/plain text (possibly an error page), not JSON.

### 12. Connection

Good programs also handle failures instead of assuming parsing always succeeds.

## Example 5 — Error handling (`05_error_handling.py`)

### 1. What are we trying to build?

A safe GET helper that reports a request problem instead of crashing unclearly.

### 2. Why do we need it?

Networks, URLs, servers, and credentials can all fail.

### 3. Architecture

```text
request -> success -> status
        -> failure -> RequestException -> clear message
```

### 4. Before code

`raise_for_status()` treats 4xx/5xx responses as errors. `RequestException` is a base class for common `requests` failures.

### 5. Code

See `05_error_handling.py`.

### 6. Important lines

The `try` contains the request; `except requests.RequestException` handles connection, timeout, and HTTP errors.

### 7. Run

```powershell
.\.venv\Scripts\python.exe requests\05_error_handling.py
```

### 8. Expected output

A readable failure message for the deliberately requested `404` endpoint.

### 9. What changed?

The program now has a controlled failure path.

### 10. Experiment

Pass a successful URL to `get_status`.

### 11. Common errors

Do not catch bare `Exception`; it can hide programming mistakes unrelated to HTTP.

### 12. Connection

Timeouts are one important failure type worth making explicit.

## Example 6 — Timeout (`06_timeout.py`)

### 1. What are we trying to build?

A request that stops waiting after a chosen limit.

### 2. Why do we need it?

Without a timeout, a stalled service can make a user wait indefinitely.

### 3. Architecture

```text
slow server -> timeout limit -> Timeout exception -> program continues
```

### 4. Before code

`timeout` is a client-side waiting limit, not an instruction that makes the server finish faster.

### 5. Code

See `06_timeout.py`.

### 6. Important lines

The specific `requests.Timeout` branch gives a clearer explanation than a generic failure.

### 7. Run

```powershell
.\.venv\Scripts\python.exe requests\06_timeout.py
```

### 8. Expected output

Usually `Timed out after 1.0 second(s).` The public service/proxy may instead fail or return promptly; both outcomes are handled.

### 9. What changed?

Error handling now distinguishes slow responses from other request failures.

### 10. Experiment

Set `timeout_seconds` to `5` and compare the behavior.

### 11. Common errors

Do not use an unrealistically tiny timeout in production; choose it for the service and user experience.

### 12. Connection

The same POST, JSON, headers, and timeout ideas apply to an LLM API.

## Example 7 — LLM API (`07_llm_api.py`)

### 1. What are we trying to build?

Send a chat message to an OpenAI-compatible LLM endpoint and print generated text.

### 2. Why do we need it?

An LLM API is still an HTTP API: it receives a POST body and returns JSON.

### 3. Architecture

```text
Python -> requests POST -> LLM API -> JSON response -> generated text
```

### 4. Before code

Copy `.env.example` values into your shell environment; do not commit a real `.env`. `LLM_BASE_URL` should omit the trailing slash and `LLM_MODEL` is provider-specific.

### 5. Code

See `07_llm_api.py`.

### 6. Important lines

`os.getenv` reads configuration; `Authorization: Bearer ...` authenticates; `messages` is the chat input. The extraction matches the OpenAI-compatible chat-completions response shape.

### 7. Run

```powershell
$env:LLM_BASE_URL = "https://api.openai.com/v1"
$env:LLM_API_KEY = "your-key"
$env:LLM_MODEL = "your-model"
.\.venv\Scripts\python.exe requests\07_llm_api.py
```

### 8. Expected output

A non-deterministic one-sentence explanation of HTTP.

### 9. What changed?

We use POST, JSON, headers, errors, and timeouts together against a credentialed API.

### 10. Experiment

Change the prompt to request an explanation for a first-year student.

### 11. Common errors

Missing variables cause a clear `RuntimeError`; `401` generally means an invalid/missing key; `429` means rate limited; a provider may use a different endpoint or response schema.

### 12. Connection

One API call is stateless unless the application deliberately sends earlier messages too.

## Example 8 — Conversation history (`08_conversation_history.py`)

### 1. What are we trying to build?

Keep a small list of chat messages and resend it with each new request.

### 2. Why do we need it?

An LLM does not automatically remember previous HTTP requests. The application must choose, store, and supply context.

### 3. Architecture

```text
user message -> application history -> LLM API -> reply -> history updated
```

### 4. Before code

Each history item has a `role` and `content`. The second request includes the first user message and first assistant reply.

### 5. Code

See `08_conversation_history.py`.

### 6. Important lines

`history.append(...)` records messages. Passing `history` as `messages` makes context explicit. In a real application, limit or summarize history to manage cost and privacy.

### 7. Run

Use the same three environment variables as Example 7, then:

```powershell
.\.venv\Scripts\python.exe requests\08_conversation_history.py
```

### 8. Expected output

The model should identify `Priya` on the second turn, though wording varies.

### 9. What changed?

We changed a one-turn call into an application-managed multi-turn conversation.

### 10. Experiment

Add a third question and inspect `conversation` before and after it.

### 11. Common errors

Do not log sensitive conversation history carelessly. If the provider response differs from the documented shape, inspect its JSON before indexing it.

### 12. Connection

FastAPI can expose these client capabilities through an API endpoint for other applications.

## Instructor Teaching Script

1. Ask: “How can one program ask another program for data?” Draw `Python -> HTTP request -> server -> response`.
2. Establish GET as asking and POST as sending. Run Examples 1–2 and ask students to identify the URL, method, body, and response.
3. Draw headers beside—not inside—the body. Ask why credentials belong in a header and why a key must not be committed.
4. Compare raw `text` with parsed `json()`. Ask students why structured data helps software.
5. Deliberately run the 404 and timeout examples. Correct the misconception that successful networking is guaranteed.
6. Draw the LLM flow and say: “The model is special, but the integration is HTTP.” Emphasize that conversation memory belongs to the application.
7. Ask before moving on: “If `requests` calls an API, what could create an API for other programs?” Expected answer: FastAPI.

## Common questions

**Is `requests` an API?** No. It is a Python client library used to call APIs.

**Does REST require JSON?** No, but JSON is common in REST-style APIs.

**Should every GET have a body?** No; use query parameters for small GET inputs, and follow the API’s documentation.

**Is an API key the same as encryption?** No. It identifies/authorizes a caller; HTTPS protects data in transit.

**Does conversation history mean an LLM has permanent memory?** No. This example sends an in-memory list with each request.

## Student Exercises

1. Change Example 1 to print a different public page’s status code.
2. Add a field to the POST JSON body and observe the echo.
3. Add a harmless custom header to Example 3.
4. Turn `get_status` into a function that returns `True`/`False` for a URL list.
5. Add a system message that makes the conversation respond in bullet points.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: requests` | Wrong interpreter or packages not installed | Run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`. |
| `ConnectionError` | Offline network, DNS, firewall, or proxy | Check connectivity/proxy settings; retry later. |
| `ReadTimeout` | Server is slower than the chosen limit | Increase the timeout only when appropriate. |
| `401` | Missing/invalid API key | Set `LLM_API_KEY` securely and verify provider instructions. |
| `404` | Wrong endpoint URL | Check the API documentation and base URL. |
| `429` | Rate limit exceeded | Wait, reduce calls, or follow the provider’s rate-limit guidance. |
| Missing LLM variable error | Environment variable was not set in this shell | Set all three variables shown in Example 7 and rerun. |

## Module boundary

This module is intentionally client-side only. It does not create FastAPI, LangChain, LangGraph, shared, test, or docs modules. Those are later phases in the prescribed learning sequence.

## Student code-reading guide

Read each file top-to-bottom, then trace the request and response: **01** imports `requests`, performs GET, checks the status, and prints raw `text`; **02** creates a Python `payload`, sends it with `json=`, and parses the echoed JSON; **03** constructs a headers dictionary and proves headers travel separately from the body; **04** uses `response.json()` and dictionary keys; **05** wraps request/HTTP/network failures in `RequestException`; **06** handles the narrower `Timeout` failure before general request errors; **07** reads environment configuration, builds authorization headers and a chat-completions JSON body, then extracts the provider response; **08** appends user and assistant messages to application-owned history before each call. Every `if __name__ == "__main__"` block is a runnable demonstration, while the functions above it make the important behavior reusable and testable.
