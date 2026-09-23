import os
from langchain_openai import ChatOpenAI

def build_model() -> ChatOpenAI:
    model = os.getenv("LLM_MODEL", "")
    if not os.getenv("LLM_API_KEY") or not model:
        raise RuntimeError("Set LLM_API_KEY and LLM_MODEL before calling a real model.")
    return ChatOpenAI(model=model, temperature=0)

if __name__ == "__main__":
    try: print(build_model())
    except RuntimeError as error: print(f"Configuration check: {error}")
