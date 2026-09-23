# `langchain`: composing LLM application components

LangChain is not an LLM. An LLM generates language; LangChain composes the application pieces around it: prompts, models, parsers, documents, retrieval, and tools.

```text
Input -> Prompt -> Model -> Parser -> Output
Question -> Retriever -> Context -> Prompt -> Model -> Answer
```

Install with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`. Run each example from the repository root: `.\.venv\Scripts\python.exe langchain\NN_name.py`.

## Ordered examples

### 01 Model

Problem: an application needs a provider model interface. Architecture: `application -> ChatOpenAI -> LLM provider`. Before code: LangChain does not supply intelligence; `ChatOpenAI` is an adapter. Important line: `ChatOpenAI(model=...)` constructs a model. Run `01_model.py`; without credentials its expected output is a safe configuration error. Experiment: set `LLM_API_KEY` and `LLM_MODEL`, then call `invoke` yourself. Common error: never hardcode the key. Connection: templates make prompts reusable.

### 02 Prompt template

Problem: repeated hard-coded prompts. Architecture: `variables -> PromptTemplate -> prompt text`. `PromptTemplate` fills `{topic}` and `{audience}` at runtime. Run `02_prompt_template.py`; it prints a beginner HTTP request. Experiment: change audience. Error: every template variable needs a value. Connection: model output needs parsing.

### 03 Output parser

Problem: model messages are objects, while applications often need text. Architecture: `AIMessage -> StrOutputParser -> string`. Run `03_output_parser.py`; it prints parsed text. The parser is the important boundary. Experiment: use another message. Connection: chains connect pieces.

### 04 Chain

Problem: manual handoffs are repetitive. Architecture: `input -> prompt -> local model -> parser`. `|` composes LangChain runnables. Run `04_chain.py`; it prints deterministic offline text. Experiment: change topic. The local model is only a credential-free stand-in. Connection: software often needs predictable fields.

### 05 Structured output

Problem: free-form text is hard for software to consume. Architecture: `JSON -> PydanticOutputParser -> Lesson`. Run `05_structured_output.py`; it prints a validated lesson. The Pydantic schema defines required fields and allowed difficulty. Experiment: use `advanced` and observe validation failure. Connection: models often need information from documents.

### 06 Documents and loaders

Problem: information can live in our own files. Architecture: `text file -> TextLoader -> Document`. Run `06_document_loader.py`; it prints local workshop notes. Experiment: edit notes. Error: verify file path/encoding. Connection: large documents must be split.

### 07 Text splitter

Problem: documents may exceed useful context. Architecture: `Document -> splitter -> overlapping chunks`. Run `07_text_splitter.py`; it prints chunks. `chunk_size` and `chunk_overlap` influence retrieval. Experiment: adjust them. Connection: embeddings turn chunks into numbers.

### 08 Embeddings

Problem: similarity search needs vectors. Architecture: `text -> embedding model -> vector`. Run `08_embeddings.py`; it prints a six-number keyword vector. This deliberately local vector is not a real semantic embedding model; embeddings are useful but not perfect understanding. Connection: a vector store keeps vectors with source documents.

### 09 Vector store

Problem: vectors need nearest-neighbor lookup. Architecture: `documents -> embeddings -> InMemoryVectorStore -> similar document`. Run `09_vector_store.py`; it finds the FastAPI document. Experiment: add a document. Connection: retrievers give applications a simpler retrieval interface.

### 10 Retriever

Problem: applications need relevant chunks. Architecture: `question -> retriever -> documents`. Run `10_retriever.py`; it retrieves the requests document. `k` controls how many chunks are returned. Connection: RAG puts retrieved context into a model prompt.

### 11 RAG

Problem: answer with external, current context. Architecture: `question -> retriever -> context -> prompt -> model -> answer`. Run `11_rag.py`; it prints the grounded prompt so it is fully local. Replace that final step with the configured model only when credentials are available. RAG retrieves context at runtime; it does not train a PDF into a model. Fine-tuning changes model behavior/parameters. Connection: tools enable actions.

### 12 Tool calling

Problem: a model may need an action, not only text. Architecture: `user -> model decision -> tool -> result -> model`. Run `12_tool_calling.py`; it prints `42`. `@tool` gives a callable a name and schema; this example invokes it directly rather than pretending a model chose it. Experiment: add subtraction. Connection: branching and tool loops need LangGraph.

## Instructor Teaching Script

Ask: “What repeats after an LLM call?” Draw `prompt -> model -> parser`. Run 02–05 before mentioning RAG. Then draw `question -> retriever -> chunks -> prompt -> model`; ask why RAG differs from training. Finally run the tool and ask who decides whether it is needed. That control-flow question introduces LangGraph.

## Common mistakes and troubleshooting

- `ModuleNotFoundError`: reinstall with the project `.venv` interpreter.
- Provider configuration error: set `LLM_API_KEY` and `LLM_MODEL`; never commit them.
- Parser error: output failed the Pydantic schema.
- Weak retrieval: inspect chunks and use a real embedding model in production; the keyword embedding is only a local teaching fallback.
- Misconception: LangChain is orchestration, not the LLM; RAG is retrieval, not fine-tuning.

## Student Exercises

1. Add a prompt variable. 2. Add a `Lesson` field. 3. Change chunk size. 4. Add and retrieve a document. 5. Add another tool.

## Connection to LangGraph

A chain is a sequence of components. Branching, shared state, retries, and model-directed tool loops require graph-based control flow, which is the next phase.
