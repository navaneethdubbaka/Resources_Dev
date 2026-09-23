# LangChain — Composing LLM Applications

> This module builds from individual model components to prompt templates, output parsers, runnable chains, validated structures, documents, retrieval, RAG-style prompts, and callable tools.

The examples use local deterministic stand-ins wherever possible, so students can learn the composition patterns without an API key. Only the first file constructs a real ChatOpenAI model and checks its credentials before doing so.

## Learning objectives

- Configure a LangChain ChatOpenAI model safely.
- Build reusable prompt templates.
- Extract text from model messages.
- Connect components with the pipe operator.
- Parse model-shaped JSON into a Pydantic schema.
- Load and split local documents.
- Create local keyword embeddings, a vector store, and a retriever.
- Ground a prompt with retrieved context.
- Define and invoke a typed tool.

## Big picture

~~~mermaid
flowchart LR
    Q[Question or input] --> P[Prompt template]
    P --> M[Model or local runnable]
    M --> O[Output parser]
    D[Local documents] --> S[Text splitter]
    S --> E[Embeddings]
    E --> V[In-memory vector store]
    V --> R[Retriever]
    R --> C[Context for RAG prompt]
    C --> P
    T[Typed tool] --> A[Agent-ready capability]
~~~

## Before the code

| Term | Meaning in this module |
| --- | --- |
| Model | A component that receives messages and returns a model response. |
| Prompt template | A reusable string template filled with runtime values. |
| Runnable | A LangChain component with an invoke method that can be composed. |
| Output parser | Converts model output into a useful Python representation. |
| Document | Text plus optional metadata used for loading and retrieval. |
| Embedding | A numeric vector representing text for similarity comparison. |
| Vector store | Storage that finds documents similar to a query vector. |
| Retriever | A simple interface that returns relevant documents. |
| RAG | Retrieval-augmented generation: retrieve context, then include it in a prompt. |
| Tool | A typed callable capability that an LLM or application can invoke. |

> [!NOTE]
> The local KeywordEmbeddings class is intentionally simple and deterministic. It marks the presence of six vocabulary words. It demonstrates the embedding/vector-store interface; it is not a semantic production embedding model.

## Setup

Run from this folder so imports of _local_support resolve:

~~~powershell
Set-Location langchain
~~~

For example, run the prompt template with:

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 02_prompt_template.py
~~~

Dependencies used by the examples are already in the virtual environment: langchain-core, langchain-openai, langchain-community, langchain-text-splitters, and pydantic.

---

## Supporting module — Local keyword embeddings

### What are we learning?

How the local retrieval examples implement LangChain’s Embeddings interface without downloading a model or calling an API.

### Why do we need it?

Examples 08–11 need repeatable vectors. This helper keeps the lesson offline and makes retrieval behavior visible.

### Code

~~~python
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
~~~

### Important lines

- VOCABULARY fixes the six vector dimensions and their order.
- The regular expression extracts lowercase alphabetic words; rstrip("s") makes simple plurals match.
- _vector produces 1.0 when a vocabulary word is present and 0.0 otherwise.
- embed_documents and embed_query supply the methods the LangChain interface needs.

### Connection

08 displays one query vector. 09 and 10 use the class for similarity search and retrieval; 11 uses it to select RAG context.

---

## 01 — Configure a model

### What are we learning?

How to construct ChatOpenAI only after checking required model credentials.

### Why do we need it?

A model client needs a model name and an API key. Failing early creates a clear setup error instead of attempting a malformed live call.

### Flow

~~~text
Environment variables → build_model() → ChatOpenAI(model, temperature=0)
                         ↓ missing values
                    clear RuntimeError
~~~

### Code

~~~python
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
~~~

### Important lines

- os.getenv reads configuration from the environment rather than source code.
- The guard requires both LLM_API_KEY and LLM_MODEL.
- temperature=0 asks for less variable model behavior.
- The main block catches the setup error to make this demo run safely without a key.

### Execution flow

With variables absent, the script prints the configuration message and exits normally. With both present, it prints the constructed ChatOpenAI object; this file does not invoke the model.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 01_model.py
~~~

### Expected output

Without the two variables:

~~~text
Configuration check: Set LLM_API_KEY and LLM_MODEL before calling a real model.
~~~

### What changed from the previous example?

This is the starting point.

### Try it yourself

With legitimate credentials in your environment, run it again and inspect the printed model object. Do not put a key in the file.

---

## 02 — Prompt template

### What are we learning?

How to define a reusable prompt with named placeholders.

### Why do we need it?

Templates separate stable instructions from changing input, avoiding repeated string construction.

### Flow

~~~text
Template + topic + audience → formatted prompt string
~~~

### Code

~~~python
from langchain_core.prompts import PromptTemplate
prompt = PromptTemplate.from_template("Explain {topic} to a {audience}.")
if __name__ == "__main__": print(prompt.format(topic="HTTP", audience="beginner"))
~~~

### Important lines

- from_template discovers topic and audience as input variables.
- format fills those placeholders and returns a normal string.

### Execution flow

The template is created, formatted with HTTP and beginner, then printed. No model call occurs.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 02_prompt_template.py
~~~

### Expected output

~~~text
Explain HTTP to a beginner.
~~~

### What changed from the previous example?

Example 01 configured a potential model. This example prepares reusable text that could become that model’s input.

### Try it yourself

Format the same template with topic FastAPI and audience API client.

---

## 03 — Output parser

### What are we learning?

How StrOutputParser extracts the text content from an AIMessage.

### Why do we need it?

Models produce message objects. A downstream component may only need the displayed string.

### Flow

~~~text
AIMessage(content) → StrOutputParser → plain string
~~~

### Code

~~~python
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
if __name__ == "__main__": print(StrOutputParser().invoke(AIMessage(content="Parsed model text.")))
~~~

### Important lines

- AIMessage is a local stand-in for a model response.
- invoke passes the message to the parser.
- StrOutputParser returns its content as text.

### Execution flow

The script creates one message, parses it, and prints only its content.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 03_output_parser.py
~~~

### Expected output

~~~text
Parsed model text.
~~~

### What changed from the previous example?

Example 02 produced a prompt string. This example handles the other side of a model interaction: turning a message response into usable text.

### Try it yourself

Change the AIMessage content and verify that the parser returns it.

---

## 04 — Compose a chain

### What are we learning?

How the pipe operator connects a prompt, runnable model-like component, and output parser.

### Why do we need it?

Composition turns separately testable pieces into a single component that can be invoked with input.

### Flow

~~~mermaid
flowchart LR
    I[topic input] --> P[PromptTemplate]
    P --> M[RunnableLambda local model]
    M --> O[StrOutputParser]
    O --> R[plain text]
~~~

### Code

~~~python
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
prompt = PromptTemplate.from_template("Explain {topic} in one sentence.")
local_model = RunnableLambda(lambda value: AIMessage(content=f"Offline model received: {value.text}"))
chain = prompt | local_model | StrOutputParser()
if __name__ == "__main__": print(chain.invoke({"topic": "FastAPI"}))
~~~

### Important lines

- RunnableLambda creates a local runnable instead of making a network model call.
- value is the prompt value produced by PromptTemplate; value.text contains its formatted text.
- | sends output from one component to the next.
- chain.invoke supplies the topic dictionary to the first component.

### Execution flow

The topic formats the prompt. The local runnable wraps that prompt in AIMessage. StrOutputParser extracts the content, which the script prints.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 04_chain.py
~~~

### Expected output

~~~text
Offline model received: Explain FastAPI in one sentence.
~~~

### What changed from the previous example?

Examples 02 and 03 showed a template and parser separately. This example connects both around a deterministic local model.

### Try it yourself

Invoke the chain with another topic and trace what each pipe stage receives.

---

## 05 — Structured output

### What are we learning?

How PydanticOutputParser converts JSON text into a validated Lesson model.

### Why do we need it?

Plain text is easy to display but difficult to process reliably. A schema makes expected fields and allowed values explicit.

### Flow

~~~text
JSON text → PydanticOutputParser(Lesson) → validated Lesson object
~~~

### Code

~~~python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
class Lesson(BaseModel):
    topic: str
    summary: str
    difficulty: str = Field(pattern="^(beginner|intermediate)$")
if __name__ == "__main__":
    print(PydanticOutputParser(pydantic_object=Lesson).parse('{"topic":"JSON","summary":"Structured text data.","difficulty":"beginner"}'))
~~~

### Important lines

- Lesson declares three required fields.
- difficulty accepts only beginner or intermediate.
- parse reads JSON text and validates it as Lesson.

### Execution flow

The hard-coded JSON matches the schema, so the parser returns and prints a Lesson object.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 05_structured_output.py
~~~

### Expected output

~~~text
topic='JSON' summary='Structured text data.' difficulty='beginner'
~~~

### What changed from the previous example?

Example 04 produced plain text. This example introduces an explicit structured result and validation.

### Try it yourself

Change difficulty to advanced and observe the parser validation failure.

---

## 06 — Load a local document

### What are we learning?

How TextLoader turns a local text file into a LangChain Document.

### Why do we need it?

Retrieval begins with source material. A loader standardizes that source into document objects.

### Flow

~~~text
data/workshop_notes.txt → TextLoader → Document → page_content
~~~

### Code

~~~python
from pathlib import Path
from langchain_community.document_loaders import TextLoader
if __name__ == "__main__":
    print(TextLoader(Path(__file__).parent / "data" / "workshop_notes.txt", encoding="utf-8").load()[0].page_content)
~~~

### Important lines

- Path(__file__).parent makes the data path work relative to this script.
- TextLoader reads the UTF-8 file.
- load() returns a document list; [0].page_content accesses the first document’s text.

### Execution flow

The script locates workshop_notes.txt beside the code, loads it as one Document, and prints the document text.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 06_document_loader.py
~~~

### Expected output

The four workshop notes about requests, FastAPI, LangChain, and LangGraph are printed.

### What changed from the previous example?

Example 05 parsed structured model-shaped output. This example introduces external source text that later examples will retrieve.

### Try it yourself

Add one line to the supplied notes locally, run again, then restore the file when finished.

---

## 07 — Split a document into chunks

### What are we learning?

How RecursiveCharacterTextSplitter divides a loaded document into overlapping chunks.

### Why do we need it?

Long documents are rarely sent or embedded as one giant unit. Chunks give retrieval a smaller, more relevant unit of context.

### Flow

~~~text
TextLoader documents → RecursiveCharacterTextSplitter
                         chunk_size=70, chunk_overlap=10
                      → numbered chunks
~~~

### Code

~~~python
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
if __name__ == "__main__":
    documents = TextLoader(Path(__file__).parent / "data" / "workshop_notes.txt", encoding="utf-8").load()
    for number, chunk in enumerate(RecursiveCharacterTextSplitter(chunk_size=70, chunk_overlap=10).split_documents(documents), 1): print(f"Chunk {number}: {chunk.page_content}")
~~~

### Important lines

- It uses the same loaded source from example 06.
- chunk_size=70 sets the target character limit.
- chunk_overlap=10 preserves ten characters between neighboring chunks.
- split_documents returns Document chunks.
- enumerate(..., 1) gives displayed chunk numbers starting at one.

### Execution flow

The notes are loaded, split, and each chunk’s page_content is printed. The current short source produces four readable chunks.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 07_text_splitter.py
~~~

### Expected output

Four numbered chunks, one for each current workshop note.

### What changed from the previous example?

Example 06 had one full Document. This script splits that document into retrieval-sized pieces.

### Try it yourself

Set chunk_size to 40 and compare the number and boundaries of chunks.

---

## 08 — Create local embeddings

### What are we learning?

How a query becomes a numeric vector using the helper’s fixed vocabulary.

### Why do we need it?

Vector stores compare vectors rather than raw text. This concrete, local example makes that transformation inspectable.

### Flow

~~~text
FastAPI builds an API → vocabulary membership → [0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
~~~

### Code

~~~python
from _local_support import KeywordEmbeddings, VOCABULARY
if __name__ == "__main__": print("Vocabulary:", VOCABULARY, "\nEmbedding:", KeywordEmbeddings().embed_query("FastAPI builds an API"))
~~~

### Important lines

- VOCABULARY supplies the dimensions and their order.
- embed_query uses KeywordEmbeddings from the support module.
- FastAPI and API produce 1.0 in their corresponding dimensions; the other vocabulary entries produce 0.0.

### Execution flow

The script prints the vocabulary tuple, then prints the six-value vector for the query.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 08_embeddings.py
~~~

### Expected output

~~~text
Vocabulary: ('python', 'fastapi', 'api', 'requests', 'langchain', 'langgraph')
Embedding: [0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
~~~

### What changed from the previous example?

Example 07 produced text chunks. This script provides a deterministic way to represent text numerically for similarity comparison.

### Try it yourself

Embed a query mentioning requests and LangGraph. Identify the positions that become 1.0.

---

## 09 — Store and search documents

### What are we learning?

How InMemoryVectorStore stores document vectors and returns the most similar document.

### Why do we need it?

An embedding alone is not retrieval. A vector store keeps document vectors and compares a query against them.

### Flow

~~~mermaid
flowchart LR
    D[Two Document objects] --> E[KeywordEmbeddings]
    E --> V[InMemoryVectorStore]
    Q[How do I build an API?] --> E
    E --> V
    V --> R[Best matching document]
~~~

### Code

~~~python
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from _local_support import KeywordEmbeddings
if __name__ == "__main__":
    store = InMemoryVectorStore(KeywordEmbeddings())
    store.add_documents([Document(page_content="FastAPI builds APIs."), Document(page_content="LangChain composes LLM components.")])
    print(store.similarity_search("How do I build an API?", k=1)[0].page_content)
~~~

### Important lines

- Document wraps each text record.
- InMemoryVectorStore holds vectors only in this Python process.
- add_documents embeds and adds both documents.
- similarity_search with k=1 asks for one closest result.
- [0].page_content prints that document’s text.

### Execution flow

The store indexes two local Documents. The query shares FastAPI/API vocabulary with the first document, so that document is returned and printed.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 09_vector_store.py
~~~

### Expected output

~~~text
FastAPI builds APIs.
~~~

### What changed from the previous example?

Example 08 displayed one vector. This example uses those vectors to choose a relevant document.

### Try it yourself

Change the query to mention LangChain and verify which stored document is returned.

---

## 10 — Use a retriever

### What are we learning?

How to adapt a vector store into a retriever and invoke it with a question.

### Why do we need it?

A retriever provides a simple, standard retrieval interface. Other chains can use it without knowing vector-store details.

### Flow

~~~text
Documents → InMemoryVectorStore → as_retriever(k=1) → invoke(question) → relevant Document
~~~

### Code

~~~python
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from _local_support import KeywordEmbeddings
if __name__ == "__main__":
    store = InMemoryVectorStore(KeywordEmbeddings())
    store.add_documents([Document(page_content="requests calls APIs."), Document(page_content="LangGraph manages workflow state.")])
    print(store.as_retriever(search_kwargs={"k": 1}).invoke("Which library calls APIs?")[0].page_content)
~~~

### Important lines

- as_retriever exposes the store through the retrieval interface.
- search_kwargs sets k to one result.
- invoke accepts the natural-language query.
- The returned list contains Document objects.

### Execution flow

The two documents are indexed. The query shares requests and API vocabulary with the first, so the retriever returns and prints requests calls APIs.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 10_retriever.py
~~~

### Expected output

~~~text
requests calls APIs.
~~~

### What changed from the previous example?

Example 09 called similarity_search directly. This example uses the retriever wrapper, which is easier to plug into larger applications.

### Try it yourself

Query for workflow state and inspect the returned document.

---

## 11 — Build a local RAG-style prompt

### What are we learning?

How retrieval supplies context that is inserted into a prompt alongside a question.

### Why do we need it?

RAG grounds a model prompt in selected source information rather than asking it to answer only from its general training.

### Flow

~~~mermaid
flowchart LR
    Q[Question] --> R[Retriever]
    D[Local documents] --> R
    R --> C[Top document page_content]
    C --> P[PromptTemplate]
    Q --> P
    P --> A[Grounded prompt text]
~~~

### Code

~~~python
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
~~~

### Important lines

- answer creates a fresh in-memory store for its two source documents.
- The retriever selects one document and extracts page_content as context.
- PromptTemplate formats context and question together.
- The function returns a prompt, not an LLM-generated answer; no model is called.

### Execution flow

The question retrieves requests calls APIs from Python. That text and the question are inserted into a prompt instructing a future model to use only context. The formatted prompt is printed.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 11_rag.py
~~~

### Expected output

~~~text
Context: requests calls APIs from Python.
Question: What calls APIs from Python?
Answer using only context.
~~~

### What changed from the previous example?

Example 10 returned a Document. This example consumes that retrieved text to construct an explicitly grounded prompt. It stops before a model invocation.

### Try it yourself

Ask what builds APIs. Check the retrieved context before describing what a model would be asked to do.

---

## 12 — Define and call a tool

### What are we learning?

How the tool decorator turns a typed Python function into a LangChain tool that can be invoked with structured arguments.

### Why do we need it?

Tools give an LLM application capabilities beyond text generation: calculations, lookups, APIs, and more.

### Flow

~~~text
Typed Python function + docstring → @tool → structured invoke input → result
~~~

### Code

~~~python
from langchain_core.tools import tool
@tool
def multiply(first: int, second: int) -> int:
    """Multiply two integers."""
    return first * second
if __name__ == "__main__": print(multiply.invoke({"first": 6, "second": 7}))
~~~

### Important lines

- @tool creates a LangChain tool from multiply.
- Type hints describe the two integer inputs and integer return.
- The docstring describes the tool’s purpose.
- invoke receives a dictionary that matches the parameter names.

### Execution flow

The tool receives 6 and 7, calls the original Python function, and prints 42. No model decides to call it in this example.

### Run

~~~powershell
Set-Location langchain
..\.venv\Scripts\python.exe 12_tool_calling.py
~~~

### Expected output

~~~text
42
~~~

### What changed from the previous example?

Example 11 prepared grounded context for a model. This example adds an application capability a model or program could invoke.

### Try it yourself

Change the invoke dictionary to multiply two other integers. Then deliberately omit one key and observe the argument validation behavior.

---

## Learning progression

~~~mermaid
flowchart LR
    A[01<br/>Model config] --> B[02<br/>Prompt]
    B --> C[03<br/>Text parser]
    C --> D[04<br/>Chain]
    D --> E[05<br/>Structured output]
    E --> F[06<br/>Load document]
    F --> G[07<br/>Split text]
    G --> H[08<br/>Embeddings]
    H --> I[09<br/>Vector store]
    I --> J[10<br/>Retriever]
    J --> K[11<br/>RAG prompt]
    K --> L[12<br/>Tool]
~~~

The module first composes model-facing pieces, then builds the retrieval pipeline, then introduces a typed callable capability. The helper module enables examples 08–11 offline.

## Code → concept

| File | Concept | What it teaches |
| --- | --- | --- |
| _local_support.py | Local embeddings | Deterministic six-keyword vectors. |
| 01_model.py | Model configuration | Build ChatOpenAI only with required environment values. |
| 02_prompt_template.py | Prompt | Fill named placeholders. |
| 03_output_parser.py | Text parser | Extract content from AIMessage. |
| 04_chain.py | Runnable chain | Pipe prompt, local model, parser. |
| 05_structured_output.py | Pydantic parser | Validate JSON against Lesson. |
| 06_document_loader.py | Loader | Read workshop notes as a Document. |
| 07_text_splitter.py | Splitter | Chunk the loaded document. |
| 08_embeddings.py | Query embedding | Inspect keyword vector output. |
| 09_vector_store.py | Similarity search | Return nearest stored document. |
| 10_retriever.py | Retriever | Invoke store through retrieval interface. |
| 11_rag.py | RAG prompt | Insert retrieved context into a prompt. |
| 12_tool_calling.py | Tool | Invoke a typed decorated function. |

## Common errors

<details>
<summary><strong>ModuleNotFoundError: _local_support</strong></summary>

~~~text
Problem: examples 08–11 cannot import the local helper
↓
Why it happens: the script was run from outside langchain/
↓
How to fix: Set-Location langchain, then run ..\.venv\Scripts\python.exe followed by the script name
~~~
</details>

<details>
<summary><strong>Configuration check in 01_model.py</strong></summary>

~~~text
Problem: the script says LLM_API_KEY and LLM_MODEL must be set
↓
Why it happens: it intentionally prevents creation of a real model client without both values
↓
How to fix: set legitimate values in the current shell; never add the key to source control
~~~
</details>

<details>
<summary><strong>Structured-output parsing failure</strong></summary>

~~~text
Problem: PydanticOutputParser rejects edited JSON
↓
Why it happens: a field is absent, has the wrong type, or difficulty is not beginner or intermediate
↓
How to fix: make the JSON match every Lesson field and its validation rule
~~~
</details>

<details>
<summary><strong>Unexpected retrieval result</strong></summary>

~~~text
Problem: local search returns a surprising document
↓
Why it happens: KeywordEmbeddings only checks six vocabulary words; it does not understand meaning beyond those exact tokens
↓
How to fix: inspect VOCABULARY and query words; use a semantic embedding provider for production systems
~~~
</details>

<details>
<summary><strong>Missing workshop_notes.txt</strong></summary>

~~~text
Problem: examples 06–07 cannot load their text file
↓
Why it happens: data/workshop_notes.txt was moved, renamed, or deleted
↓
How to fix: restore it under langchain/data/; the code resolves its location relative to the script
~~~
</details>

## Instructor teaching flow

~~~text
START
 ↓
Bridge from FastAPI: “Now we will compose the intelligence behind an endpoint.”
 ↓
Explain model, prompt, parser, runnable, document, embedding, retriever, RAG, tool
 ↓
Run 01 and discuss safe configuration
 ↓
Run 02–04; trace text through prompt, local model, and parser
 ↓
Run 05; change a constrained field to show schema validation
 ↓
Run 06–07; inspect source text and chunk boundaries
 ↓
Run 08–10; map keyword vectors to similarity and retrieval
 ↓
Run 11; emphasize it creates a grounded prompt, not a model answer
 ↓
Run 12; show a typed capability a model could use
~~~

Useful questions:

- Why does the model example check configuration even though it does not invoke the model?
- What is gained by using PromptTemplate instead of f-strings everywhere?
- What does the pipe operator make easier to test or reuse?
- Why should a JSON answer be parsed into a schema?
- Why split a document before retrieval?
- Why is this keyword embedding useful for teaching but weak for production?
- What is the difference between a vector store and a retriever?
- Does example 11 call an LLM? What does it produce instead?
- What information makes multiply a useful tool contract?

## Student exercises

~~~text
Easy → Small modification → Concept combination
~~~

1. **Easy:** Reformat the prompt in example 02 for another topic and audience.
2. **Small modification:** Change the local chain topic in example 04 and trace each stage.
3. **Small modification:** Add an allowed difficulty value by updating the Lesson pattern and JSON in example 05.
4. **Small modification:** Change chunk_size in example 07 and compare chunks.
5. **Concept combination:** Add one vocabulary word to _local_support.py, embed a query containing it, and create a matching document for example 09.
6. **Concept combination:** Add a third document to example 10, then design a query that retrieves it.
7. **Concept combination:** Add a retrieved source to example 11 and verify its context is selected for a matching question.
8. **Tool extension:** Define a second typed arithmetic tool using the pattern in example 12.

## Key takeaways

- LangChain components are composable runnables with clear inputs and outputs.
- Prompts organize variable text; parsers turn model-shaped output into reliable values.
- Pydantic schemas make structured output enforceable.
- Load, split, embed, store, and retrieve are distinct retrieval stages.
- RAG means adding selected context to a prompt; it does not inherently guarantee a live model call.
- Tools expose typed Python capabilities to an LLM application.
- Local stand-ins can make a workflow testable without credentials or network access.

## Connection to the next module

~~~mermaid
flowchart LR
    A[LangChain] --> B[“I can compose LLM components.”]
    B --> C[LangGraph]
    C --> D[“I can control state, branches, and loops.”]
~~~

LangChain focuses on components and linear composition. The next module, langgraph/, adds explicit stateful workflow control.
