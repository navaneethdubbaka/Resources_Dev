# Beginner Student Guide

Read code in this order: imports, data, functions/routes, then the direct-run block. Predict each line before running it.

## Requests

`01_get_request.py` sends GET, receives a response object, checks error status, then prints status/body. `02_post_request.py` turns a Python dictionary into JSON with `json=`, then parses returned JSON. `03_headers.py` sends metadata such as `Accept`; headers are not the body. `04_json_request.py` converts JSON text into a Python dictionary. `05_error_handling.py` places fallible network work in `try` and catches request-specific failures. `06_timeout.py` catches a timeout before broader failures. `07_llm_api.py` reads secrets from environment variables, sends authenticated JSON, and extracts provider response text. `08_conversation_history.py` appends each user/assistant message and resends the list: the application, not the LLM, owns memory.

## FastAPI

Every file creates `app`; Uvicorn serves it. A decorator maps an HTTP method/path to the function beneath it. `01` returns a dictionary as JSON. `02` maps `{user_id}` URL text to a typed function input. `03` reads `?query=` values and applies defaults. `04` reads a JSON body. `05` uses Pydantic fields to reject invalid input before route code executes. `06` returns a deliberate 404 with `HTTPException`. `07` validates chat input, checks configuration, calls the provider, and maps setup/provider failures to safe HTTP errors.

## LangChain

Follow examples in number order. `01` constructs a provider adapter but does not make it intelligent. `02` fills prompt placeholders. `03` converts a message object into plain text. `04` pipes prompt, local stand-in model, and parser. `05` validates structured JSON with Pydantic. `06` loads a local file into `Document`; `07` splits it; `08` turns text into a teaching vector; `09` stores/searches vectors; `10` exposes retrieval; `11` inserts retrieved context into a prompt; `12` describes and invokes a tool. RAG retrieves runtime context; it does not train a model.

## LangGraph

Think “executable flowchart.” State is the notebook carried between nodes; a node returns state updates; edges choose execution order. `01` is a line; `02` demonstrates state; `03` separates work into nodes; `04` orders nodes; `05` branches; `06` loops with a stopping counter; `07` routes to a tool; `08` checkpoints by thread ID; `09` is developer-defined workflow; `10` loops agent -> tool -> agent until no tool is needed.
