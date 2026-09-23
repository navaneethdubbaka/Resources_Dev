from typing import TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): topic: str; outline: str; result: str
def outline(s: State): return {"outline":f"Introduction to {s['topic']}"}
def write(s: State): return {"result":s["outline"]+": a short lesson."}
g=StateGraph(State); g.add_node("create_outline",outline); g.add_node("write",write); g.add_edge(START,"create_outline"); g.add_edge("create_outline","write"); g.add_edge("write",END)
if __name__ == "__main__": print(g.compile().invoke({"topic":"graphs","outline":"","result":""}))
