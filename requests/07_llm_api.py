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
