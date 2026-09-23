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
