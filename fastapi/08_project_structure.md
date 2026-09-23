# Phase 2 project structure

Each numbered file is deliberately an independent FastAPI application. That keeps live demonstrations small: start exactly one file with Uvicorn, make a request, then stop it before starting the next.

```text
fastapi/
├── 01_hello_api.py          # one GET route
├── 02_path_parameters.py    # values inside a URL path
├── 03_query_parameters.py   # values after ? in a URL
├── 04_post_request.py       # unstructured JSON body
├── 05_pydantic_models.py    # validated JSON body
├── 06_error_handling.py     # intentional 404 response
├── 07_llm_endpoint.py       # credential-safe LLM bridge
└── 08_project_structure.md
```

For example, run the hello application from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn 01_hello_api:app --app-dir fastapi --reload
```

The `--app-dir fastapi` option tells Uvicorn where the numbered modules live. The later `shared/` folder is intentionally not created in this phase.
