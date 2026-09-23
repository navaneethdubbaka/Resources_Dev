from typing import TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): steps: list[str]
def first(state: State): return {"steps": state["steps"] + ["first"]}
def second(state: State): return {"steps": state["steps"] + ["second"]}
graph=StateGraph(State); graph.add_node("first",first); graph.add_node("second",second)
graph.add_edge(START,"first"); graph.add_edge("first","second"); graph.add_edge("second",END)
if __name__ == "__main__": print(graph.compile().invoke({"steps":[]}))
