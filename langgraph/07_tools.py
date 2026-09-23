from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): request: str; result: str
def decide(s: State): return {}
def route(s: State) -> Literal["tool",END]: return "tool" if s["request"].startswith("add ") else END
def calculator(s: State): return {"result":str(sum(map(int,s["request"].split()[1:])))}
g=StateGraph(State); g.add_node("decide",decide); g.add_node("tool",calculator); g.add_edge(START,"decide"); g.add_conditional_edges("decide",route); g.add_edge("tool",END)
if __name__ == "__main__": print(g.compile().invoke({"request":"add 6 7","result":""}))
