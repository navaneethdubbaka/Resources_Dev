from pathlib import Path
from langchain_community.document_loaders import TextLoader
if __name__ == "__main__":
    print(TextLoader(Path(__file__).parent / "data" / "workshop_notes.txt", encoding="utf-8").load()[0].page_content)
