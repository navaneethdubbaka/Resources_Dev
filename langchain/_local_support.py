import re
from langchain_core.embeddings import Embeddings

VOCABULARY = ("python", "fastapi", "api", "requests", "langchain", "langgraph")

class KeywordEmbeddings(Embeddings):
    def _vector(self, text: str) -> list[float]:
        words = {word.rstrip("s") for word in re.findall(r"[a-z]+", text.lower())}
        return [float(word in words) for word in VOCABULARY]
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]
    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)
