from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from _local_support import KeywordEmbeddings
if __name__ == "__main__":
    store = InMemoryVectorStore(KeywordEmbeddings())
    store.add_documents([Document(page_content="requests calls APIs."), Document(page_content="LangGraph manages workflow state.")])
    print(store.as_retriever(search_kwargs={"k": 1}).invoke("Which library calls APIs?")[0].page_content)
