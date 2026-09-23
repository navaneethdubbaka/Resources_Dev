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
