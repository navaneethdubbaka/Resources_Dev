from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
if __name__ == "__main__":
    documents = TextLoader(Path(__file__).parent / "data" / "workshop_notes.txt", encoding="utf-8").load()
    for number, chunk in enumerate(RecursiveCharacterTextSplitter(chunk_size=70, chunk_overlap=10).split_documents(documents), 1): print(f"Chunk {number}: {chunk.page_content}")
