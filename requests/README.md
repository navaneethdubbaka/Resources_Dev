# Python requests — Calling HTTP APIs

> A teachable progression from a basic HTTP GET request to an authenticated, multi-turn OpenAI-compatible LLM client.

Read the scripts in numerical order. Each one introduces a single capability used by a later example.

## Learning objectives

- Make GET and POST requests with requests.
- Send JSON bodies and HTTP headers.
- Parse JSON responses and select fields.
- Check HTTP errors and handle timeouts.
- Configure a chat-completions client through environment variables.
- Keep multi-turn chat context by sending conversation history.

## Big picture

~~~mermaid
flowchart LR
    P[Python application] --> R[requests]
    R -->|GET / POST + timeout| API[HTTP API]
    API -->|status + headers + body| R
    R -->|text or JSON| P
    ENV[LLM_BASE_URL<br/>LLM_API_KEY<br/>LLM_MODEL] -. configures .-> R
    P -->|messages| LLM[OpenAI-compatible<br/>chat completions API]
~~~

## Before the code

| Term | Meaning in these scripts |
| --- | --- |
| API | A service that another program can use over a network. |
| HTTP | The request/response protocol being used. |
| Endpoint | One API URL, such as https://httpbin.org/post. |
| Request | Client input: method, URL, plus optional headers and body. |
| Response | Server output: status code, headers, and body. |
| JSON | Structured data represented in Python as dictionaries and lists. |
| Timeout | The maximum time a client will wait. |

> [!TIP]
> A 404 or 500 is still a requests response. Calling response.raise_for_status() turns it into an exception that a program can deliberately handle.

## Setup

The existing virtual environment contains the only direct dependency:

~~~powershell
.\.venv\Scripts\python.exe -m pip show requests
~~~

Run scripts from the repository root:

~~~powershell
.\.venv\Scripts\python.exe requests\01_get_request.py
~~~

Examples 01–06 need internet access. Examples 07–08 also need valid LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL values. Never put a secret key in source code.

---

## 01 — Smallest useful GET request

### What are we learning?

How to retrieve a page with requests.get(), validate the status, and read text.

### Why do we need it?

GET is the starting point for retrieving a resource from most APIs.

### Flow

~~~text
Python → requests.get() → HTTP GET → example.com → 200 + HTML → response.text
~~~

### Code

~~~python
"""Make the smallest useful HTTP GET request."""

import requests


def main() -> None:
    response = requests.get("https://example.com", timeout=10)
    response.raise_for_status()

    print("Status code:", response.status_code)
    print("First 200 characters of the response:")
    print(response.text[:200])


if __name__ == "__main__":
    main()
~~~

### Important lines

- requests.get(...) sends the request and returns a Response.
- timeout=10 prevents indefinite waiting.
- raise_for_status() validates the response status.
- response.text is the body as text; [:200] shortens only the displayed output.

### Execution flow

The program requests Example Domain, checks success, prints status 200, then prints the first 200 characters of HTML.

### Run

~~~powershell
.\.venv\Scripts\python.exe requests\01_get_request.py
~~~

### Expected output

Status code 200 followed by the beginning of the Example Domain HTML. The exact text can change.

### What changed from the previous example?

This is the starting point.

### Try it yourself

Change [:200] to [:50]. What changes, and what does not?

---

## 02 — POST a JSON body

### What are we learning?

How to send a Python dictionary as JSON with POST and decode a JSON reply.

### Why do we need it?

Many APIs require client input: a record to create, a form submission, or a prompt.

### Flow

~~~mermaid
sequenceDiagram
    participant P as Python
    participant A as httpbin.org/post
    P->>A: POST with json=payload
    A-->>P: 200 + JSON echo
    P->>P: response.json()["json"]
~~~

### Code

~~~python
"""Send a JSON request body with HTTP POST."""

import requests


def main() -> None:
    payload = {"name": "Ada", "topic": "HTTP POST"}
    response = requests.post("https://httpbin.org/post", json=payload, timeout=10)
    response.raise_for_status()

    data = response.json()
    print("Server received this JSON:", data["json"])


if __name__ == "__main__":
    main()
~~~

### Important lines

- payload is a normal Python dictionary.
- json=payload serializes and sends it as a JSON body.
- response.json() parses the JSON response.
- data["json"] selects the server echo.

### Execution flow

The script posts Ada’s data to httpbin, checks the response, and prints the JSON the server received.

### Run

~~~powershell
.\.venv\Scripts\python.exe requests\02_post_request.py
~~~

### Expected output

~~~text
Server received this JSON: {'name': 'Ada', 'topic': 'HTTP POST'}
~~~

### What changed from the previous example?

Example 01 retrieved text with GET. This example sends structured JSON with POST and parses structured JSON back.

### Try it yourself

Add "level": "beginner" to payload and verify it is echoed.

---

## 03 — Send request headers

### What are we learning?

How to attach request metadata through HTTP headers.

### Why do we need it?

Headers describe client preferences, identity, and eventually authorization; they are separate from the body.

### Flow

~~~text
headers dictionary → requests.get(..., headers=headers) → httpbin → echoed headers
~~~

### Code

~~~python
"""Send descriptive metadata with request headers."""

import requests


def main() -> None:
    headers = {
        "Accept": "application/json",
        "User-Agent": "ai-engineering-day2/1.0",
    }
    response = requests.get("https://httpbin.org/headers", headers=headers, timeout=10)
    response.raise_for_status()

    print("Headers seen by the server:")
    print(response.json()["headers"])


if __name__ == "__main__":
    main()
~~~

### Important lines

- Accept asks for JSON.
- User-Agent identifies this client.
- headers=headers attaches the dictionary to the GET.
- httpbin /headers returns what it saw; transport layers may add more headers.

### Execution flow

The script sends both headers, validates the response, parses its JSON, and prints the server-visible header dictionary.

### Run

~~~powershell
.\.venv\Scripts\python.exe requests\03_headers.py
~~~

### Expected output

A dictionary containing Accept: application/json and User-Agent: ai-engineering-day2/1.0, plus extra transport headers.

### What changed from the previous example?

Example 02 used a request body. This GET adds metadata through headers—the mechanism later used for LLM authorization.

### Try it yourself

Change User-Agent and locate the new value in the response.

---

## 04 — Read JSON fields

### What are we learning?

How to parse an API JSON response and select named values from the resulting dictionary.

### Why do we need it?

Printing a whole response is useful for exploration; applications need the particular fields they use.

### Flow

~~~text
GET /todos/1 → JSON response → response.json() → Python dictionary → selected fields
~~~

### Code

~~~python
"""Read JSON returned by an API and access its fields."""

import requests


def main() -> None:
    response = requests.get("https://jsonplaceholder.typicode.com/todos/1", timeout=10)
    response.raise_for_status()

    data = response.json()
    print("Whole JSON object:", data)
    print("Title:", data["title"])
    print("Completed:", data["completed"])


if __name__ == "__main__":
    main()
~~~

### Important lines

- The endpoint represents a sample todo item.
- .json() converts the body into a Python dictionary.
- data["title"] and data["completed"] select individual values.

### Execution flow

The program retrieves todo 1, shows the whole object, then prints its title and completed flag.

### Run

~~~powershell
.\.venv\Scripts\python.exe requests\04_json_request.py
~~~

### Expected output

The current sample includes title delectus aut autem and Completed: False.

### What changed from the previous example?

Example 03 inspected echoed request metadata. This example treats returned JSON as application data.

### Try it yourself

Change /todos/1 to /todos/2 and compare its fields.

---

## 05 — Handle HTTP and network failures

### What are we learning?

How to catch requests.RequestException so a failed request becomes a controlled program outcome.

### Why do we need it?

Servers can return error statuses and networks can fail. A client needs a deliberate failure path.

### Flow

~~~mermaid
flowchart TD
    A[get_status(url)] --> B[GET + timeout]
    B --> C{raise_for_status succeeds?}
    C -->|Yes| D[Print success; return status]
    C -->|No| E[Catch RequestException]
    E --> F[Print failure; return None]
~~~

### Code

~~~python
"""Handle network, timeout, and HTTP-status failures safely."""

import requests


def get_status(url: str) -> int | None:
    """Return a successful status code, or explain why the request failed."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return None

    print(f"Request succeeded with status {response.status_code}")
    return response.status_code


if __name__ == "__main__":
    # This endpoint intentionally returns 404 so the error path is visible.
    get_status("https://httpbin.org/status/404")
~~~

### Important lines

- int | None declares either a successful status or no value.
- The try includes both request and status validation.
- RequestException covers request-related errors, including the one raised by raise_for_status().
- This endpoint intentionally returns 404.

### Execution flow

The request gets a 404. raise_for_status() raises, the except block prints the failure, and the function returns None. The script exits normally.

### Run

~~~powershell
.\.venv\Scripts\python.exe requests\05_error_handling.py
~~~

### Expected output

Output starts with Request failed: and reports a 404 Client Error. This is the intended path and exits with code 0.

### What changed from the previous example?

The earlier scripts assumed success. This one turns an unsuccessful response into a safe, explicit outcome.

### Try it yourself

Import get_status and call it with https://example.com. Compare the successful integer with the 404 result.

---

## 06 — Set a short timeout

### What are we learning?

How to handle requests.Timeout separately from other request failures.

### Why do we need it?

Without a timeout, a slow service can leave an application waiting too long.

### Flow

~~~text
httpbin delay: 3 seconds → client timeout: 1.0 second → Timeout → print message → False
~~~

### Code

~~~python
"""Set a time limit so a slow server cannot block the program forever."""

import requests


def get_with_short_timeout(url: str, timeout_seconds: float = 1.0) -> bool:
    try:
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.Timeout:
        print(f"Timed out after {timeout_seconds} second(s).")
        return False
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return False

    print("Request completed before the timeout.")
    return True


if __name__ == "__main__":
    # httpbin waits three seconds; the one-second timeout demonstrates the failure.
    get_with_short_timeout("https://httpbin.org/delay/3")
~~~

### Important lines

- timeout_seconds: float = 1.0 provides a configurable one-second default.
- The specific Timeout handler appears before broad RequestException.
- /delay/3 intentionally exceeds the allowed second.

### Execution flow

The endpoint delays for three seconds; requests raises Timeout after one. The function prints a precise message and returns False.

### Run

~~~powershell
.\.venv\Scripts\python.exe requests\06_timeout.py
~~~

### Expected output

~~~text
Timed out after 1.0 second(s).
~~~

### What changed from the previous example?

Example 05 handled failures broadly. This example identifies the common slow-server case specifically.

### Try it yourself

Call get_with_short_timeout("https://httpbin.org/delay/3", timeout_seconds=5). Predict the result first.

---

## 07 — Call an OpenAI-compatible LLM API

### What are we learning?

How JSON, headers, timeout, configuration, and response parsing combine in an authenticated chat-completions request.

### Why do we need it?

An LLM API is an HTTP API: it needs an endpoint, authentication, a JSON payload, and defensive handling.

### Flow

~~~mermaid
sequenceDiagram
    participant E as Environment
    participant P as Python
    participant L as LLM chat-completions API
    E-->>P: base URL, key, model
    P->>L: POST + Bearer token + messages JSON
    L-->>P: choices[0].message.content
    P-->>P: print answer
~~~

### Code

~~~python
"""Call an OpenAI-compatible LLM API with configuration from environment variables."""

import os

import requests


def load_llm_config() -> tuple[str, str, str]:
    """Read required configuration without ever putting a key in source code."""
    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "")
    if not all((base_url, api_key, model)):
        raise RuntimeError(
            "Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL before running this example."
        )
    return base_url, api_key, model


def ask_llm(messages: list[dict[str, str]]) -> str:
    """Send chat messages and return text from a chat-completions response."""
    base_url, api_key, model = load_llm_config()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages}

    try:
        response = requests.post(
            f"{base_url}/chat/completions", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"LLM request failed: {error}") from error


if __name__ == "__main__":
    answer = ask_llm([{"role": "user", "content": "Explain HTTP in one sentence."}])
    print(answer)
~~~

### Important lines

- os.getenv reads configuration outside source code; rstrip("/") normalizes the URL.
- all(...) fails before a request when any required setting is missing.
- Authorization: Bearer carries the secret key; never print or commit it.
- json=payload sends the chosen model and messages.
- The response path extracts the first assistant answer.
- The exception tuple covers network/HTTP issues and an unexpected JSON shape.

### Execution flow

The script validates configuration, POSTs to {LLM_BASE_URL}/chat/completions, checks success, extracts the assistant content, and prints it. Missing configuration stops execution before a request.

### Run

Set valid provider-specific values in the current PowerShell session:

~~~powershell
$env:LLM_BASE_URL = "https://your-provider.example/v1"
$env:LLM_API_KEY = "your-secret-key"
$env:LLM_MODEL = "your-model-name"
.\.venv\Scripts\python.exe requests\07_llm_api.py
~~~

### Expected output

With valid values, it prints a one-sentence answer. If any configuration is missing, it intentionally raises:

~~~text
RuntimeError: Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL before running this example.
~~~

### What changed from the previous example?

The safe HTTP patterns are now used in a real authenticated API: headers, JSON body, 30-second timeout, and nested JSON parsing.

### Try it yourself

With valid configuration, change only the user prompt and observe the answer.

---

## 08 — Preserve conversation history

### What are we learning?

How to create multi-turn context by appending user and assistant messages to a list and sending all history on every request.

### Why do we need it?

HTTP requests are independent. The client must resupply prior turns if the model should use them as context.

### Flow

~~~mermaid
flowchart LR
    S[system instruction] --> H[conversation history]
    U1[first user turn] --> H
    H -->|POST all messages| L[LLM API]
    L --> A1[assistant reply]
    A1 --> H
    U2[second user turn] --> H
    H -->|POST expanded history| L
~~~

### Code

~~~python
"""Show that an application must send chat history if it wants context."""

import os

import requests


def load_llm_config() -> tuple[str, str, str]:
    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "")
    if not all((base_url, api_key, model)):
        raise RuntimeError(
            "Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL before running this example."
        )
    return base_url, api_key, model


def send_message(history: list[dict[str, str]], user_message: str) -> str:
    """Add a user message, call the API with all history, then save its reply."""
    base_url, api_key, model = load_llm_config()
    history.append({"role": "user", "content": user_message})
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": history},
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": answer})
    return answer


if __name__ == "__main__":
    conversation: list[dict[str, str]] = [
        {"role": "system", "content": "Answer clearly and briefly."}
    ]
    print("Assistant:", send_message(conversation, "My name is Priya."))
    print("Assistant:", send_message(conversation, "What is my name?"))
    print("Messages sent on the second request:", len(conversation))
~~~

### Important lines

- conversation begins with a system instruction.
- history.append adds the user turn before the request.
- messages: history sends every accumulated message, not only the newest.
- The returned assistant answer is appended for future context.
- After two turns, len(conversation) is normally 5: system, user, assistant, user, assistant.

### Execution flow

The first request sends the instruction and introduction, then stores the reply. The second adds the name question and sends the enlarged history, allowing the model to use the earlier introduction.

### Run

After setting the same three variables from example 07:

~~~powershell
.\.venv\Scripts\python.exe requests\08_conversation_history.py
~~~

### Expected output

Two assistant replies are printed. With a capable configured model, the second identifies Priya. The final line normally is:

~~~text
Messages sent on the second request: 5
~~~

The exact model wording can vary. Missing configuration produces the intentional RuntimeError shown in example 07.

### What changed from the previous example?

Example 07 sends a message list once. This script maintains that list across calls and records both sides of every turn.

### Try it yourself

Add a third call asking what instruction the assistant was given. Predict the final history length.

---

## Learning progression

~~~mermaid
flowchart LR
    A[01<br/>GET text] --> B[02<br/>POST JSON]
    B --> C[03<br/>Headers]
    C --> D[04<br/>Read JSON]
    D --> E[05<br/>Failures]
    E --> F[06<br/>Timeouts]
    F --> G[07<br/>LLM API]
    G --> H[08<br/>Conversation history]
~~~

| New example | Why it is introduced |
| --- | --- |
| 01 | Establishes the request/response cycle. |
| 02 | Adds JSON flowing from client to server. |
| 03 | Adds request metadata. |
| 04 | Uses response JSON as program data. |
| 05 | Handles a failed request safely. |
| 06 | Distinguishes a slow request from other failures. |
| 07 | Combines prior pieces in a configured LLM call. |
| 08 | Adds client-managed state across LLM turns. |

## Code → concept

| File | Concept | What it teaches |
| --- | --- | --- |
| 01_get_request.py | GET and text | Request, validate, inspect a text response. |
| 02_post_request.py | POST JSON | Send a dictionary and parse JSON. |
| 03_headers.py | Headers | Send metadata visible to the server. |
| 04_json_request.py | JSON fields | Select useful values from an API response. |
| 05_error_handling.py | Failures | Catch RequestException and return None. |
| 06_timeout.py | Timeout | Catch a slow-request failure. |
| 07_llm_api.py | LLM client | Configure and call chat completions securely. |
| 08_conversation_history.py | Conversation state | Send full history on each request. |

## Common errors

<details>
<summary><strong>ModuleNotFoundError: No module named requests</strong></summary>

~~~text
Problem: Python cannot import requests
↓
Why it happens: a different interpreter is running, or requests is absent there
↓
How to fix: use .\.venv\Scripts\python.exe and run
            .\.venv\Scripts\python.exe -m pip show requests
~~~
</details>

<details>
<summary><strong>Connection, DNS, proxy, or firewall failure</strong></summary>

~~~text
Problem: requests cannot reach a public endpoint
↓
Why it happens: internet access, proxy/firewall rules, DNS, or service availability blocks the connection
↓
How to fix: check network/proxy configuration and retry; retain timeouts and error handling in real clients
~~~
</details>

<details>
<summary><strong>404 in example 05 / timeout in example 06</strong></summary>

~~~text
Problem: example 05 prints a 404, or example 06 prints a timeout
↓
Why it happens: both endpoints deliberately trigger the demonstrated error path
↓
How to fix: no fix is needed; use these outputs to trace the relevant except branch
~~~
</details>

<details>
<summary><strong>Missing LLM configuration in examples 07–08</strong></summary>

~~~text
Problem: RuntimeError requests LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL
↓
Why it happens: the script refuses to make an LLM request without all required configuration
↓
How to fix: set valid provider-specific values in the current shell; never commit a key
~~~
</details>

<details>
<summary><strong>LLM 401, 404, or unexpected response shape</strong></summary>

~~~text
Problem: the LLM request fails
↓
Why it happens: invalid key, incorrect endpoint/model, or a provider that is not OpenAI-compatible at /chat/completions
↓
How to fix: verify the provider endpoint, authentication, model name, and expected response format
~~~
</details>

## Instructor teaching flow

~~~text
START
 ↓
Ask: “How can one program ask another program for data?”
 ↓
Explain API, endpoint, request, response, and JSON
 ↓
Show the architecture diagram
 ↓
Open 01; identify URL, timeout, status check, and text
 ↓
Run and change the output slice
 ↓
Open and run 02–04; compare body, headers, and returned fields
 ↓
Open and run 05–06; treat failure as a normal program state
 ↓
Open 07; map each HTTP piece to the LLM request
 ↓
Explain environment variables and secret safety
 ↓
Open 08; trace the growing history list
 ↓
Ask what happens if prior messages are omitted
 ↓
Move to FastAPI
~~~

Useful teaching questions:

- What does raise_for_status() protect us from?
- Why use json=payload rather than manually composing JSON text?
- Which information belongs in a header rather than a request body?
- Why does example 05 exit successfully after an HTTP failure?
- Why is Timeout caught before RequestException in example 06?
- Which three LLM settings must stay out of source code?
- Why can the second LLM turn refer to Priya?

## Student exercises

~~~text
Easy → Small modification → Concept combination
~~~

1. **Easy:** Change example 01 to print 50 characters.
2. **Small modification:** Add a field to example 02’s JSON and verify the echo.
3. **Small modification:** Set another User-Agent in example 03 and locate it in the response.
4. **Small modification:** Request a different todo ID in example 04 and print its fields.
5. **Concept combination:** Call get_status() with both a successful URL and its 404 URL; handle its int | None result.
6. **Concept combination:** Call example 06’s function with one and five seconds; predict both outcomes.
7. **LLM extension:** With valid configuration, add a third turn to example 08 and predict the final history length.

## Key takeaways

- APIs communicate through HTTP requests and responses.
- GET retrieves; POST can send JSON.
- Headers carry metadata, including authorization.
- Parse JSON, then access the fields a program needs.
- Use raise_for_status(), exception handling, and timeouts.
- Keep LLM keys and connection settings in environment variables.
- HTTP is stateless; client-sent history creates chat context.

## Connection to the next module

~~~mermaid
flowchart LR
    A[requests] --> B[“I can CALL an API.”]
    B --> C[FastAPI]
    C --> D[“Now I will BUILD an API.”]
~~~

This module makes Python the **client**. The next folder, fastapi/, makes Python the **server** that defines endpoints and returns responses.
