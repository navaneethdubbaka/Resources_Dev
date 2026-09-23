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
