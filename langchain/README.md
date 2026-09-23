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

## Detailed code walkthroughs

### `01_model.py`

`os.getenv` reads configuration from the current shell instead of source code. `build_model` refuses to create a usable provider client until both `LLM_API_KEY` and `LLM_MODEL` exist. `ChatOpenAI(model=model, temperature=0)` is the LangChain provider adapter; it does not make a network call when constructed. The `__main__` guard means this demonstration runs only when the file is executed directly. Its `try`/`except` turns absent credentials into a teaching message rather than exposing a secret or producing an unclear traceback.

### `02_prompt_template.py`

`PromptTemplate.from_template(...)` records a reusable string with two named placeholders. `prompt.format(...)` replaces them with the supplied keyword values and returns ordinary text. No model is involved yet: this isolates prompt construction so students can see that templates are reusable text, not intelligence.

### `03_output_parser.py`

`AIMessage` represents a model-style response object. `StrOutputParser` accepts that object and returns only its text `content`. This demonstrates why parsers matter: the rest of an application should receive the output shape it needs instead of provider-specific message objects.

### `04_chain.py`

The prompt turns `topic` input into a `PromptValue`. `RunnableLambda` is a deterministic offline stand-in that reads `value.text` and produces an `AIMessage`; it is deliberately not an LLM. The pipe operator builds one runnable sequence: prompt output flows to model output, then to `StrOutputParser`. `chain.invoke` supplies the one input dictionary and returns the final string.

### `05_structured_output.py`

`Lesson` is a Pydantic schema: `topic` and `summary` are required strings; `difficulty` is restricted by a regular-expression pattern. `PydanticOutputParser` converts JSON text into a validated `Lesson` instance. If a field is absent, malformed, or has an unsupported difficulty, parsing raises a validation error—exactly the predictable failure a program needs.

### `06_document_loader.py`

`Path(__file__).parent` locates this module reliably regardless of the terminal's current directory. `TextLoader(..., encoding="utf-8")` reads the local text file and returns LangChain `Document` objects. `page_content` is the source text; loaders can also carry metadata. The example uses a local file so no download or API key is needed.

### `07_text_splitter.py`

The loader first produces documents, then `RecursiveCharacterTextSplitter` divides them into chunks near 70 characters while preserving a 10-character overlap. The loop labels each resulting chunk. Overlap lets related boundary text appear in adjacent chunks; too much overlap repeats data, while too little can split necessary context.

### `08_embeddings.py`

`VOCABULARY` defines six teaching dimensions. `KeywordEmbeddings.embed_query` lowercases and singularizes words, then returns `1.0` for present vocabulary words and `0.0` otherwise. It makes the text-to-vector transformation visible, but it is not a replacement for a trained semantic embedding model and should not be used for production retrieval.

### `09_vector_store.py`

Each `Document` stores source text. `InMemoryVectorStore(KeywordEmbeddings())` pairs documents with vectors in process memory; `add_documents` creates those vectors. `similarity_search(query, k=1)` embeds the query, compares it with stored vectors, and returns the nearest one document. The store disappears when the program stops.

### `10_retriever.py`

The store setup is the same as Example 9, but `as_retriever(search_kwargs={"k": 1})` exposes a retrieval-focused interface. `retriever.invoke(question)` returns documents rather than a final answer. Separating retrieval from generation lets an application inspect, cite, filter, or format the retrieved context before an LLM sees it.

### `11_rag.py`

`answer` creates a small local document collection, retrieves the single nearest chunk, and assigns its `page_content` to `context`. The prompt template combines context and the original question, explicitly directing a later model to use only that context. Printing the prompt is intentional: it reveals the RAG handoff without claiming that a local template itself generated an answer. A real model call belongs after this visible boundary.

### `12_tool_calling.py`

`@tool` reads the function name, type hints, and docstring to create a LangChain tool with a schema. `multiply.invoke` calls that tool using a dictionary whose keys match the parameter names. This is direct invocation, not autonomous model choice; it teaches the tool contract before LangGraph adds routing and loops.
