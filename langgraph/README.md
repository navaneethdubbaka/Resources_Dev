# `langgraph`: stateful workflows and agents

LangChain composes components in a sequence. LangGraph is for cases where the control flow needs state, branching, loops, retries, tools, or memory.

## If you are completely new

Imagine a flowchart that can execute Python functions. A box is a **node**; an arrow is an **edge**; the notebook carried between boxes is the **state**. Start with Example 1 and trace the arrows on paper before executing it. Do not start with the agent: Examples 1–9 build the vocabulary needed to understand why Example 10 returns from a tool to an agent node.

```text
START -> node -> edge -> node -> END
                 \-> conditional route -> another node
```

State is shared information such as user input, messages, decisions, and results. Nodes are functions that read/update state; edges choose what runs next.

Run every example with `.\.venv\Scripts\python.exe langgraph\NN_name.py`.

## Examples

| File | Problem / architecture / result | Key idea and experiment |
| --- | --- | --- |
| `01_linear_graph.py` | A -> greeting node -> END; prints a greeting state. | A minimal compiled graph. Change the greeting. |
| `02_state.py` | input state -> process node -> result state; prints upper-case input. | Nodes return state updates. Add another field. |
| `03_nodes.py` | prefix node -> suffix node -> END; prints reviewed text. | Nodes are small units of work. Swap their order. |
| `04_edges.py` | START -> first -> second -> END; prints ordered steps. | Edges define execution sequence. Add a third node. |
| `05_conditional_edges.py` | classifier -> answer or calculator -> END; `add 2 3` prints `5`. | Conditional routing creates branching. Try a question. |
| `06_loops.py` | generate -> check -> generate or END; prints two attempts. | Loops support retries/validation. Change the threshold. |
| `07_tools.py` | decide -> calculator tool or END; prints `13`. | A graph controls a deterministic tool path. |
| `08_memory_checkpoint.py` | state -> increment -> memory checkpoint; prints count 1. | `MemorySaver` associates state with a `thread_id`; it is in-memory, not durable storage. |
| `09_workflow.py` | outline -> write -> END; prints a short lesson. | A workflow has developer-defined control flow. |
| `10_basic_agent.py` | agent -> tool? -> calculator -> agent -> END; prints answer `42`. | An agent loop allows a decision step after a tool result. |

## Example 1: `01_linear_graph.py` line-by-line beginner walkthrough

```python
from typing import TypedDict
```

`TypedDict` lets us describe the expected keys and value types in a dictionary. It helps readers and type-checking tools understand the state shape. It does not create a database and it does not force values at runtime by itself.

```python
from langgraph.graph import END, START, StateGraph
```

`StateGraph` is the LangGraph object used to describe a workflow whose nodes share state. `START` is a special built-in marker meaning “the graph begins here.” `END` is a special marker meaning “the graph finishes here.” They are not ordinary functions written by the student.

```python
class State(TypedDict):
    text: str
```

This declares that state moving through this graph has one named field: `text`, containing a string. Think of state as a small notebook passed between workflow steps. At the start, the notebook contains `{"text": "AI Engineering"}`. A node may read the notebook and return changes to it.

```python
def greet(state: State):
```

This defines a node function named `greet`. LangGraph will call it later; defining it does not run it immediately. The `state: State` annotation tells students that the incoming dictionary should follow the state shape above.

```python
    return {"text": f"Hello, {state['text']}"}
```

`state["text"]` reads the current text from the state dictionary. The `f` before the string creates an f-string, allowing the value to be inserted between `Hello, ` and the end of the text. The function returns a **partial state update**. LangGraph merges this returned `text` value into the current state notebook. It does not need to mutate a global variable.

```python
graph = StateGraph(State)
```

This creates an unfinished graph definition and tells LangGraph which state shape it will use. At this point there are no nodes or arrows, so it cannot run yet.

```python
graph.add_node("greet", greet)
```

This registers the Python function `greet` as a graph node named `"greet"`. The string is the node's graph label; the second value is the function to run when execution reaches that label.

```python
graph.add_edge(START, "greet")
graph.add_edge("greet", END)
```

An edge is an arrow in the workflow. The first edge says execution enters `greet` immediately after starting. The second says execution stops after `greet` completes. Together they form a linear graph: `START -> greet -> END`.

```python
app = graph.compile()
```

`compile()` checks the graph structure and turns the definition into an executable application object. This is similar to building a route table before a FastAPI server handles a request: the graph is now ready to receive state.

```python
if __name__ == "__main__":
    print(app.invoke({"text": "AI Engineering"}))
```

The guard means this demo runs only when the file is executed directly. `invoke` supplies the initial state dictionary. LangGraph follows `START -> greet -> END`; `greet` changes the text to `Hello, AI Engineering`; `invoke` returns the final state; `print` displays it.

**Full execution trace:** initial state `{"text": "AI Engineering"}` -> start edge -> `greet(state)` -> returned update `{"text": "Hello, AI Engineering"}` -> final state -> end. This is a deterministic workflow: the developer has defined every route, and no model/agent decides what happens next.

For each example: the problem is the limitation named in the table; inspect the small source before code execution; run the exact command above; expected output is described in the table; then perform its experiment. Common errors are covered below and each row leads to the next concept.

## Workflow versus agent

```text
Workflow: developer defines the route, for example A -> B -> C
Agent: a model/decision step can choose a tool or next action within guardrails
```

Not every graph is an agent. Examples 1–9 are deterministic workflows. Example 10 is intentionally small: its rule-based agent chooses the calculator only for `add ...` input, then returns to the agent node.

## Instructor Teaching Script

Draw a linear chain, then add a branch and a loop. Ask why a chain cannot plainly show retry or routing. Run 01–04 first; ask students to name the state, nodes, and edges. Run 05 and 06 to show decisions and cycles. Explain checkpointing after the basic graph. Finally draw `agent -> tool? -> tool -> agent` and ask why this is different from a fixed workflow.

## Debugging

- `ModuleNotFoundError: langgraph`: install with the project `.venv` interpreter.
- Graph compile error: check every reachable node and edge, including a path to `END`.
- Infinite loop: make the conditional route eventually return `END` and use a bounded counter.
- Missing state key: initialize it in the input and return updates with the expected names.
- Checkpoint confusion: `MemorySaver` is process memory; restarting the program removes it.

## Student Exercises

1. Add a third linear node. 2. Add a multiplication route. 3. Retry three times. 4. Store a second checkpointed value. 5. Add a second tool to the basic agent.

## Connection to Day 3

Day 3 can build on this control-flow foundation: real models can participate in routing, retrieval, tool choice, and memory-aware agent workflows.

## Detailed code walkthroughs

### `01_linear_graph.py`

`TypedDict` declares the state shape: this graph carries one `text` field. `greet` receives the current state and returns only the field it updates. `StateGraph(State)` creates the graph definition; `add_node` registers work, and `START -> greet -> END` defines a complete route. `compile()` makes it executable; `invoke` supplies initial state and returns final state.

### `02_state.py`

The state has input and result fields. `process` reads `user_input`, calls Python's `upper`, and returns a partial update for `result`. LangGraph merges that update into the state. This is the central state rule: nodes do not need to mutate a global variable; they return explicit updates.

### `03_nodes.py`

Two small functions are two nodes: `add_prefix` transforms text first, `add_suffix` sees that updated text second. The explicit edges establish their order. Splitting work this way makes a longer workflow inspectable and lets later graphs route to different nodes.

### `04_edges.py`

The list begins empty. `first` returns a replacement list with `first` appended; `second` receives that update and appends `second`. The result demonstrates that edges are execution instructions, not data transformations themselves.

### `05_conditional_edges.py`

`classify` is intentionally a visible decision point. `route` examines `request` and returns a node name: calculation for input beginning with `add `, otherwise answer. `add_conditional_edges` uses that return value to select the next edge. `calculate` parses the remaining whitespace-separated numbers; malformed `add` input would need validation in a real API.

### `06_loops.py`

`generate` increments the bounded `attempts` counter and writes a new draft. Its conditional edge calls `check`, which returns `generate` until two attempts exist, then returns `END`. The counter is essential: loops must have an explicit finishing condition to avoid infinite graph execution.

### `07_tools.py`

This graph separates a decision node from the calculator tool node. `route` chooses `tool` only for an addition request; otherwise it returns `END`. The tool node writes `result`, and its normal edge ends the workflow. This is deterministic control flow, not yet a model-driven agent.

### `08_memory_checkpoint.py`

`MemorySaver` is passed to `compile` as a checkpointer. `thread_id` in the configurable invocation identifies the conversation/workflow stream whose state may be saved. `increment` itself remains a normal state node. Because the saver is in memory, it is useful for concept demos but vanishes when the program exits.

### `09_workflow.py`

The `State` separates raw topic, intermediate outline, and final result. `create_outline` writes the intermediate field; `write` consumes it. The node is named differently from the `outline` state key because LangGraph reserves state keys from node names. This is a developer-authored workflow: every path is predefined.

### `10_basic_agent.py`

`agent` writes a direct answer when no tool result exists, otherwise promotes the returned tool result to `answer`. Its conditional route sends only addition requests without a prior result to `tool`. The tool writes `tool_result` and edges back to `agent`, where the route reaches `END`. That return edge is the minimal agent loop: decide, act, observe result, decide again.
