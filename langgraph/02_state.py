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
