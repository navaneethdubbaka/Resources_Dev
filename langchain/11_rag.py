from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from _local_support import KeywordEmbeddings
def answer(question: str) -> str:
    store = InMemoryVectorStore(KeywordEmbeddings())
    store.add_documents([Document(page_content="FastAPI builds APIs."), Document(page_content="requests calls APIs from Python.")])
    context = store.as_retriever(search_kwargs={"k": 1}).invoke(question)[0].page_content
    return PromptTemplate.from_template("Context: {context}\nQuestion: {question}\nAnswer using only context.").format(context=context, question=question)
if __name__ == "__main__": print(answer("What calls APIs from Python?"))
