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
