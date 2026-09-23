# LangGraph — Stateful LLM Workflows

> This module moves beyond linear LLM composition. It uses graphs to make state, steps, routing decisions, loops, tools, checkpoints, and a minimal agent workflow explicit.

Each file is a small, independent graph. The examples are deterministic: they do not require an API key or a live LLM to teach the workflow mechanics.

## Learning objectives

- Define graph state with TypedDict.
- Add node functions that update state.
- Connect nodes using linear edges.
- Route execution conditionally.
- Repeat work with a controlled loop.
- Branch to a tool-like calculator.
- Compile with an in-memory checkpoint saver.
- Build a small multi-step workflow and a basic tool-using agent loop.

## Big picture

~~~mermaid
flowchart LR
    I[Initial state] --> N[Graph node]
    N --> U[Updated state]
    U --> R{Routing decision}
    R -->|next step| N2[Another node]
    R -->|finish| E[END]
    R -->|repeat| N
    N2 --> E
~~~

## Before the code

| Term | Meaning in this module |
| --- | --- |
| State | The typed dictionary that carries information through a graph. |
| Node | A Python function that receives state and returns updates. |
| Edge | A fixed connection that determines the next node. |
| Conditional edge | A routing function chooses which connection to follow. |
| START / END | Special graph markers for beginning and stopping execution. |
| Compile | Turn a StateGraph definition into an executable app. |
| Checkpoint | A saved state snapshot associated with a thread identifier. |
| Tool node | A node that performs a capability such as calculation. |

> [!TIP]
> Nodes return only the state fields they change. LangGraph merges those returned updates into the graph’s current state.

## Setup

All examples use the existing virtual environment:

~~~powershell
.\.venv\Scripts\python.exe langgraph\01_linear_graph.py
~~~

The examples use langgraph and typing from the standard library. They do not need API keys or network access.

---

## 01 — Linear graph

### What are we learning?

How to define state, register one node, connect START to that node and then END, compile, and invoke.

### Why do we need it?

This is the smallest complete LangGraph workflow: input state enters a function and returns updated state.

### Flow

~~~mermaid
flowchart LR
    S[START] --> G[greet node]
    G --> E[END]
~~~

### Code

~~~python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    text: str

def greet(state: State):
    return {"text": f"Hello, {state['text']}"}

graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")
graph.add_edge("greet", END)
app = graph.compile()

if __name__ == "__main__":
    print(app.invoke({"text": "AI Engineering"}))
~~~

### Important lines

- State declares one required text field.
- greet reads text and returns an update to the same field.
- StateGraph(State) binds the graph to that state schema.
- add_node names the callable; edges set its execution order.
- compile creates app, whose invoke method runs the graph.

### Execution flow

The initial text is AI Engineering. START enters greet, the node prefixes it with Hello, and END returns the final state.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\01_linear_graph.py
~~~

### Expected output

~~~text
{'text': 'Hello, AI Engineering'}
~~~

### What changed from the previous example?

This is the starting point.

### Try it yourself

Change the input text and predict the final dictionary.

---

## 02 — State carries input and result

### What are we learning?

How a state schema can preserve original input while a node adds a separate result.

### Why do we need it?

Workflows often need both the original request and values created during processing.

### Flow

~~~text
initial user_input → process node → result in uppercase → final state with both fields
~~~

### Code

~~~python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    user_input: str
    result: str

def process(state: State):
    return {"result": state["user_input"].upper()}

graph = StateGraph(State)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

if __name__ == "__main__":
    print(graph.compile().invoke({"user_input": "state moves through nodes"}))
~~~

### Important lines

- State has input and result fields.
- process reads user_input but returns only result.
- LangGraph retains user_input while merging the returned result.

### Execution flow

The node converts the input sentence to uppercase. The final state includes the original lowercase user_input and the uppercase result.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\02_state.py
~~~

### Expected output

~~~text
{'user_input': 'state moves through nodes', 'result': 'STATE MOVES THROUGH NODES'}
~~~

### What changed from the previous example?

Example 01 updated its only state value. This graph retains one field and adds a different output field.

### Try it yourself

Add another state field and return an update for it from process.

---

## 03 — Multiple nodes

### What are we learning?

How multiple node functions each transform the same state field in sequence.

### Why do we need it?

Complex work is easier to understand when separated into focused steps.

### Flow

~~~mermaid
flowchart LR
    S[START] --> P[prefix node]
    P --> X[suffix node]
    X --> E[END]
~~~

### Code

~~~python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    text: str

def add_prefix(state: State): return {"text": "Draft: " + state["text"]}
def add_suffix(state: State): return {"text": state["text"] + " (reviewed)"}

graph = StateGraph(State)
graph.add_node("prefix", add_prefix); graph.add_node("suffix", add_suffix)
graph.add_edge(START, "prefix"); graph.add_edge("prefix", "suffix"); graph.add_edge("suffix", END)
if __name__ == "__main__": print(graph.compile().invoke({"text": "nodes are functions"}))
~~~

### Important lines

- add_prefix and add_suffix both return a replacement text value.
- The prefix edge is followed by the suffix edge.
- Semicolons keep several independent Python statements on one source line; the graph behavior is still sequential.

### Execution flow

The initial sentence gains Draft: in prefix, then gains (reviewed) in suffix. END returns the twice-updated text.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\03_nodes.py
~~~

### Expected output

~~~text
{'text': 'Draft: nodes are functions (reviewed)'}
~~~

### What changed from the previous example?

Example 02 had one processing node. This graph splits a transformation across two named steps.

### Try it yourself

Insert a third node between prefix and suffix that changes the text in another small way.

---

## 04 — Fixed edges

### What are we learning?

How edges define a fixed, visible order of work.

### Why do we need it?

Some workflows have no decision to make: step one always precedes step two.

### Flow

~~~mermaid
flowchart LR
    S[START] --> A[first node]
    A --> B[second node]
    B --> E[END]
~~~

### Code

~~~python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): steps: list[str]
def first(state: State): return {"steps": state["steps"] + ["first"]}
def second(state: State): return {"steps": state["steps"] + ["second"]}
graph=StateGraph(State); graph.add_node("first",first); graph.add_node("second",second)
graph.add_edge(START,"first"); graph.add_edge("first","second"); graph.add_edge("second",END)
if __name__ == "__main__": print(graph.compile().invoke({"steps":[]}))
~~~

### Important lines

- steps starts as an empty list.
- Each node returns a new list containing the existing steps plus its own name.
- The two add_edge calls enforce first before second.

### Execution flow

first returns a list containing first. second receives that updated list and appends second. The final state records both steps in order.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\04_edges.py
~~~

### Expected output

~~~text
{'steps': ['first', 'second']}
~~~

### What changed from the previous example?

Example 03 also had two nodes, but focused on text transformations. This example makes the ordered route itself visible in state.

### Try it yourself

Add a third fixed node that appends third.

---

## 05 — Conditional edges

### What are we learning?

How a routing function selects one of two next nodes from the current state.

### Why do we need it?

Workflows need decisions. A request that looks like addition should take a calculation branch; another request can take an answer branch.

### Flow

~~~mermaid
flowchart TD
    S[START] --> C[classify node]
    C --> R{Request starts with add}
    R -->|yes| K[calculate node]
    R -->|no| A[answer node]
    K --> E[END]
    A --> E
~~~

### Code

~~~python
from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): request: str; result: str
def classify(state: State): return {}
def route(state: State) -> Literal["answer","calculate"]: return "calculate" if state["request"].startswith("add ") else "answer"
def answer(state: State): return {"result":"This is a question."}
def calculate(state: State): return {"result":str(sum(map(int,state["request"].split()[1:])))}
graph=StateGraph(State); graph.add_node("classify",classify); graph.add_node("answer",answer); graph.add_node("calculate",calculate)
graph.add_edge(START,"classify"); graph.add_conditional_edges("classify",route); graph.add_edge("answer",END); graph.add_edge("calculate",END)
if __name__ == "__main__": print(graph.compile().invoke({"request":"add 2 3"}))
~~~

### Important lines

- classify returns no update, but gives the graph a decision point.
- route returns calculate when request starts with add and answer otherwise.
- Literal describes the permitted node names returned by route.
- add_conditional_edges attaches route to execution after classify.
- calculate sums the remaining space-separated request tokens.

### Execution flow

The supplied request starts with add, so route chooses calculate. It sums 2 and 3, writes result 5, then reaches END.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\05_conditional_edges.py
~~~

### Expected output

~~~text
{'request': 'add 2 3', 'result': '5'}
~~~

### What changed from the previous example?

Example 04 always followed the same edges. This graph chooses its next node based on state.

### Try it yourself

Change the request to a sentence that does not start with add. Which node is selected and what result appears?

---

## 06 — Controlled loop

### What are we learning?

How a conditional edge can revisit a node until state meets a completion condition.

### Why do we need it?

Many workflows iterate: draft, check, revise, then stop when a criterion is met.

### Flow

~~~mermaid
flowchart TD
    S[START] --> G[generate draft]
    G --> C{Attempts at least two}
    C -->|no| G
    C -->|yes| E[END]
~~~

### Code

~~~python
from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): attempts: int; draft: str
def generate(s: State): return {"attempts":s["attempts"]+1,"draft":f"draft {s['attempts']+1}"}
def check(s: State) -> Literal["generate",END]: return END if s["attempts"] >= 2 else "generate"
g=StateGraph(State); g.add_node("generate",generate); g.add_edge(START,"generate"); g.add_conditional_edges("generate",check)
if __name__ == "__main__": print(g.compile().invoke({"attempts":0,"draft":""}))
~~~

### Important lines

- generate increments attempts and labels the new draft with that count.
- check sends the graph to END once attempts is at least 2.
- Otherwise check returns generate, making the graph loop.
- The initial count of 0 guarantees exactly two generate executions.

### Execution flow

The first generate returns attempts 1 and draft 1; check loops. The second returns attempts 2 and draft 2; check routes to END.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\06_loops.py
~~~

### Expected output

~~~text
{'attempts': 2, 'draft': 'draft 2'}
~~~

### What changed from the previous example?

Example 05 routed to one final branch. This example routes back to a previous node, with state providing the stopping condition.

### Try it yourself

Change the completion check to attempts >= 3. Predict the final draft value.

---

## 07 — Route to a tool-like node

### What are we learning?

How a graph can decide whether to execute a calculator capability.

### Why do we need it?

Agents and workflows often require actions beyond text processing. A tool branch keeps that action explicit and controllable.

### Flow

~~~mermaid
flowchart TD
    S[START] --> D[decide node]
    D --> R{Request starts with add}
    R -->|yes| T[calculator tool node]
    R -->|no| E[END]
    T --> E
~~~

### Code

~~~python
from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): request: str; result: str
def decide(s: State): return {}
def route(s: State) -> Literal["tool",END]: return "tool" if s["request"].startswith("add ") else END
def calculator(s: State): return {"result":str(sum(map(int,s["request"].split()[1:])))}
g=StateGraph(State); g.add_node("decide",decide); g.add_node("tool",calculator); g.add_edge(START,"decide"); g.add_conditional_edges("decide",route); g.add_edge("tool",END)
if __name__ == "__main__": print(g.compile().invoke({"request":"add 6 7","result":""}))
~~~

### Important lines

- route chooses the node named tool only for addition requests; otherwise it returns END.
- calculator is registered under the graph node name tool.
- The calculator logic is the same simple integer summation pattern as the calculate branch in example 05.
- result begins empty because this state includes it even before the tool writes it.

### Execution flow

The sample request starts with add. The graph enters calculator, stores 13 in result, then ends. A non-add request would end after decide with its existing result.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\07_tools.py
~~~

### Expected output

~~~text
{'request': 'add 6 7', 'result': '13'}
~~~

### What changed from the previous example?

Example 06 loops one node. This graph instead makes a one-time decision to invoke or skip a capability.

### Try it yourself

Change the request to hello. What state reaches END, and why does calculator not run?

---

## 08 — In-memory checkpoint

### What are we learning?

How to compile a graph with MemorySaver and invoke it using a thread identifier.

### Why do we need it?

Checkpointing gives a stateful workflow a place to associate saved execution state with a particular conversation or task thread.

### Flow

~~~text
State plus thread ID → compiled graph with MemorySaver → increment node → returned state and checkpoint
~~~

### Code

~~~python
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
class State(TypedDict): count: int
def increment(s: State): return {"count":s["count"]+1}
g=StateGraph(State); g.add_node("increment",increment); g.add_edge(START,"increment"); g.add_edge("increment",END); app=g.compile(checkpointer=MemorySaver())
if __name__ == "__main__": print(app.invoke({"count":0},{"configurable":{"thread_id":"lesson-1"}}))
~~~

### Important lines

- MemorySaver is an in-memory checkpoint implementation.
- compile(checkpointer=MemorySaver()) enables checkpointing for app.
- configurable thread_id identifies the checkpoint thread for this invocation.
- increment returns count plus one.

### Execution flow

The graph runs increment for count 0 and returns count 1. MemorySaver is attached under the thread ID lesson-1 for this running process.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\08_memory_checkpoint.py
~~~

### Expected output

~~~text
{'count': 1}
~~~

### What changed from the previous example?

Example 07 introduced a tool branch. This example returns to a simple linear graph but adds execution persistence through a checkpointer.

### Try it yourself

Change the starting count. Then investigate how a second invocation with the same thread ID differs when using checkpoint-aware workflow features.

---

## 09 — Two-step content workflow

### What are we learning?

How state can carry a value produced by one content step into the next.

### Why do we need it?

Many LLM workflows are staged: prepare an outline, then use it to write a final result.

### Flow

~~~mermaid
flowchart LR
    S[START] --> O[create outline]
    O --> W[write lesson]
    W --> E[END]
~~~

### Code

~~~python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): topic: str; outline: str; result: str
def outline(s: State): return {"outline":f"Introduction to {s['topic']}"}
def write(s: State): return {"result":s["outline"]+": a short lesson."}
g=StateGraph(State); g.add_node("create_outline",outline); g.add_node("write",write); g.add_edge(START,"create_outline"); g.add_edge("create_outline","write"); g.add_edge("write",END)
if __name__ == "__main__": print(g.compile().invoke({"topic":"graphs","outline":"","result":""}))
~~~

### Important lines

- State keeps original topic plus intermediate outline and final result.
- create_outline is the graph node name; outline is its Python function.
- write reads the outline generated by the preceding node.
- The edges enforce outline before write.

### Execution flow

The topic graphs produces Introduction to graphs in outline. write then turns that intermediate state into the final short lesson text.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\09_workflow.py
~~~

### Expected output

~~~text
{'topic': 'graphs', 'outline': 'Introduction to graphs', 'result': 'Introduction to graphs: a short lesson.'}
~~~

### What changed from the previous example?

Example 08 added a checkpointer to one increment. This example shows a more realistic multi-step state workflow where one generated field feeds another.

### Try it yourself

Change topic to retrieval and identify every final-state field that changes.

---

## 10 — Basic tool-using agent loop

### What are we learning?

How an agent node can route to a tool, then return to the agent with the tool result.

### Why do we need it?

An agent workflow must often decide whether it has enough information to respond or should first call a capability.

### Flow

~~~mermaid
flowchart TD
    S[START] --> A[agent node]
    A --> R{Needs addition tool}
    R -->|yes| T[tool node]
    T --> A
    R -->|no| E[END]
~~~

### Code

~~~python
from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): message: str; tool_result: str; answer: str
def agent(s: State): return {"answer":s["tool_result"] or "I can answer directly."}
def route(s: State) -> Literal["tool",END]: return "tool" if s["message"].startswith("add ") and not s["tool_result"] else END
def tool(s: State): return {"tool_result":str(sum(map(int,s["message"].split()[1:])))}
g=StateGraph(State); g.add_node("agent",agent); g.add_node("tool",tool); g.add_edge(START,"agent"); g.add_conditional_edges("agent",route); g.add_edge("tool","agent")
if __name__ == "__main__": print(g.compile().invoke({"message":"add 20 22","tool_result":"","answer":""}))
~~~

### Important lines

- agent writes answer from tool_result when available; otherwise it writes a direct-answer placeholder.
- route requests tool only for an add message with no current tool_result.
- tool calculates the sum and stores it in state.
- tool connects back to agent, creating the agent-tool-agent loop.
- Once tool_result is present, route returns END and prevents an infinite loop.

### Execution flow

The first agent execution sets a direct-answer placeholder, then route sees an addition request with no tool result and enters tool. tool stores 42. The graph returns to agent, which replaces answer with 42. route now ends because tool_result is present.

### Run

~~~powershell
.\.venv\Scripts\python.exe langgraph\10_basic_agent.py
~~~

### Expected output

~~~text
{'message': 'add 20 22', 'tool_result': '42', 'answer': '42'}
~~~

### What changed from the previous example?

Example 09 was a one-way two-step workflow. This graph adds a controlled return edge: the agent runs again after the tool provides information.

### Try it yourself

Change message to a non-add request. Why does the graph finish after the first agent node, and what answer remains?

---

## Learning progression

~~~mermaid
flowchart LR
    A[01<br/>Linear graph] --> B[02<br/>State fields]
    B --> C[03<br/>Nodes]
    C --> D[04<br/>Fixed edges]
    D --> E[05<br/>Conditional routing]
    E --> F[06<br/>Loops]
    F --> G[07<br/>Tool branch]
    G --> H[08<br/>Checkpoint]
    H --> I[09<br/>Workflow]
    I --> J[10<br/>Agent loop]
~~~

| File | Concept | Why it comes next |
| --- | --- | --- |
| 01_linear_graph.py | First graph | Establishes state, node, edge, compile, invoke. |
| 02_state.py | Multiple fields | Preserves input while producing a result. |
| 03_nodes.py | Node sequence | Splits transformation into named functions. |
| 04_edges.py | Fixed path | Makes ordered work explicit. |
| 05_conditional_edges.py | Branching | Selects a path from current state. |
| 06_loops.py | Iteration | Returns to a node with a stop condition. |
| 07_tools.py | Capability branch | Calls or skips a calculator node. |
| 08_memory_checkpoint.py | Checkpoint | Associates execution with a thread. |
| 09_workflow.py | Staged generation | Passes intermediate state to a later step. |
| 10_basic_agent.py | Agent loop | Returns from a tool to an agent safely. |

## Code → concept

| File | Main graph pattern | What it teaches |
| --- | --- | --- |
| 01_linear_graph.py | START → node → END | The smallest runnable state graph. |
| 02_state.py | Input plus result | State update merging. |
| 03_nodes.py | Two transformations | Separate node responsibilities. |
| 04_edges.py | Linear sequence | Fixed execution ordering. |
| 05_conditional_edges.py | Two branches | Router-selected next node. |
| 06_loops.py | Repeated node | State-based completion. |
| 07_tools.py | Optional tool | Capability routing. |
| 08_memory_checkpoint.py | Checkpointed node | In-memory thread association. |
| 09_workflow.py | Outline then write | Intermediate workflow state. |
| 10_basic_agent.py | Agent → tool → agent | Controlled tool-use loop. |

## Common errors

<details>
<summary><strong>ModuleNotFoundError: langgraph</strong></summary>

~~~text
Problem: Python cannot import LangGraph
↓
Why it happens: the wrong Python interpreter is running
↓
How to fix: run scripts with .\.venv\Scripts\python.exe
~~~
</details>

<details>
<summary><strong>Graph never stops</strong></summary>

~~~text
Problem: a looped graph reaches a recursion limit or continues unexpectedly
↓
Why it happens: a conditional edge always routes back to a node, or its stop state is never updated
↓
How to fix: define a clear state-based completion condition, as attempts >= 2 and the tool_result check do here
~~~
</details>

<details>
<summary><strong>ValueError from the calculator examples</strong></summary>

~~~text
Problem: addition routes fail while converting request words to integers
↓
Why it happens: requests beginning with add must be followed by space-separated integer values
↓
How to fix: use input such as add 2 3; add error validation before summing in a real application
~~~
</details>

<details>
<summary><strong>Checkpoint appears not to persist</strong></summary>

~~~text
Problem: a saved state is unavailable in another process
↓
Why it happens: MemorySaver stores checkpoints only in memory for the running Python process
↓
How to fix: keep the process alive for this demo, or use a durable checkpointer for production persistence
~~~
</details>

<details>
<summary><strong>Deprecation warning during execution</strong></summary>

~~~text
Problem: LangChainPendingDeprecationWarning mentions allowed_objects
↓
Why it happens: an installed LangGraph checkpoint dependency has a future default change
↓
How to fix: the examples still run successfully; review the installed library documentation before upgrading or configuring production serializers
~~~
</details>

## Instructor teaching flow

~~~text
START
 ↓
Bridge from LangChain: “Components are useful; now we control their workflow.”
 ↓
Explain state, node, edge, START, END, and compile
 ↓
Run 01–04 and trace the evolving dictionary
 ↓
Ask students to predict state before each node
 ↓
Run 05 and compare two routing outcomes
 ↓
Run 06 and identify the loop stop condition
 ↓
Run 07 and discuss tool routing
 ↓
Run 08 and explain thread IDs and in-memory checkpoints
 ↓
Run 09 as a staged workflow
 ↓
Run 10 and trace agent → tool → agent → END
~~~

Useful questions:

- Why do nodes return dictionaries instead of mutating a global variable?
- What makes an edge fixed versus conditional?
- Which field ends the loop in example 06?
- How does example 07 avoid calling its calculator for a normal request?
- What does thread_id identify in example 08?
- Why does example 10 revisit agent but still stop?
- Which steps could later be replaced with real LLM calls?

## Student exercises

~~~text
Easy → Small modification → Concept combination
~~~

1. **Easy:** Change the greeting input in example 01.
2. **Small modification:** Add a field to state in example 02 and update it in process.
3. **Small modification:** Insert a third node into example 03 or 04.
4. **Concept combination:** Add a second route condition to example 05 for another deterministic request type.
5. **Concept combination:** Make example 06 produce three drafts rather than two.
6. **Tool workflow:** Add another small capability node based on example 07.
7. **Agent extension:** Add a state field that records whether example 10 used the tool.

## Key takeaways

- LangGraph makes workflow state and transitions explicit.
- Nodes return state updates; edges determine what runs next.
- Conditional edges create branches and loops need explicit stop conditions.
- Tools are ordinary nodes routed by state.
- Checkpoints associate workflow execution with a thread.
- An agent loop is a graph pattern: decide, use a tool if needed, then respond.

## Where this leads

~~~mermaid
flowchart LR
    A[LangChain] --> B[Compose components]
    B --> C[LangGraph]
    C --> D[Control state, branches, loops, and tools]
    D --> E[Robust AI workflows]
~~~

You now have the progression from calling APIs, to building APIs, to composing LLM components, to controlling stateful AI workflows.
