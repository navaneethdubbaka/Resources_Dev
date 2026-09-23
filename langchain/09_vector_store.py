from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from _local_support import KeywordEmbeddings
if __name__ == "__main__":
    store = InMemoryVectorStore(KeywordEmbeddings())
    store.add_documents([Document(page_content="FastAPI builds APIs."), Document(page_content="LangChain composes LLM components.")])
    print(store.similarity_search("How do I build an API?", k=1)[0].page_content)
