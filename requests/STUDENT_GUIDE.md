# Requests: detailed beginner guide

## Big picture

Your Python program is a **client**. An API or website is a **server**. The client sends a request and the server sends a response. A response has a status code (`200` success, `404` missing), headers (metadata), and a body (actual text/data). `requests` does the HTTP work for Python.

Read every file in this order: imports, variables, functions, then `if __name__ == "__main__"`. That last condition means “run this demonstration only when this exact file is executed.”

## 01_get_request.py

`import requests` loads the installed library. `requests.get(URL, timeout=10)` sends a GET request: GET means “give me data.” The URL identifies where it goes. The timeout prevents endless waiting; it does not make a server faster. The returned `response` object contains far more than page text. `raise_for_status()` turns 4xx/5xx server statuses into a Python error, so failure cannot silently look successful. `response.status_code` is the integer result. `response.text[:200]` prints the first 200 characters of HTML; slicing keeps output readable. Change the URL and predict whether its body will be HTML or JSON.

## 02_post_request.py

`payload` is a Python dictionary stored locally. POST means “here is data for you to process.” `json=payload` converts that dictionary into JSON request text and supplies the correct content-type header. After a successful response, `.json()` converts returned JSON text back into Python values. `data` is the whole returned object; `data["json"]` selects the part that proves what the server received. Add a field such as `"year": 3`; the echo should include it.

## 03_headers.py

Headers are metadata on a request, not its body. `Accept` says the client prefers JSON; `User-Agent` labels the client. `headers=headers` attaches the dictionary to the GET request. This teaching endpoint returns received headers, making the data flow visible. A real `Authorization` header can contain a secret API key: read it from an environment variable, never hardcode or commit it. A User-Agent is identification, not security.

## 04_json_request.py

JSON is text representing objects, lists, strings, numbers, booleans, or null. `.json()` parses it into Python structures; here `data` is a dictionary. `data["title"]` and `data["completed"]` select exact keys. Use `.text` when raw text matters; use `.json()` only when the server returns JSON. Missing keys raise `KeyError`; non-JSON bodies raise a parsing error. Check status before trusting fields.

## 05_error_handling.py

`get_status(url)` accepts input so it can be reused. The `try` block contains network work that may fail. Success prints and returns an integer status. A network, timeout, or HTTP error jumps to `except requests.RequestException`, prints a useful reason, and returns `None`: no successful status exists. The shown URL deliberately returns 404. Do not catch bare `Exception`; that could hide a spelling or logic bug.

## 06_timeout.py

`timeout_seconds=1.0` is a default argument. `Timeout` is caught before broad `RequestException` because it needs a specific explanation; exception order matters because Timeout is itself a request error. Both failure paths return `False`; success returns `True`, so another program can react without reading terminal text. The server may still work after the client gives up waiting.

## 07_llm_api.py

`os.getenv` reads configuration outside code. `rstrip("/")` avoids a double slash when building the endpoint. Missing base URL, key, or model raises an early `RuntimeError`. `ask_llm` builds Bearer authentication headers and a JSON body containing `model` and chat `messages`, then POSTs it. The nested `choices[0]["message"]["content"]` follows an OpenAI-compatible response shape. Provider/network/shape failures become one clear `RuntimeError`. Never commit credentials.

## 08_conversation_history.py

`history` is an application-owned list of role/content dictionaries. `send_message` appends the user message, sends all history, reads the reply, then appends the assistant reply. The second request includes the first turn, so the model can answer about Priya. This is not permanent LLM memory: context is resent on every HTTP call. More history means more cost, latency, and privacy risk; real programs limit or summarize it.

## Student self-check

For each file, point to the URL, method, headers, body, status check, returned data, and possible error path. If a line is unclear, insert `print(variable)` after it, run the example, and observe the real value.
