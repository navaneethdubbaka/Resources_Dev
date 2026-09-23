from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): attempts: int; draft: str
def generate(s: State): return {"attempts":s["attempts"]+1,"draft":f"draft {s['attempts']+1}"}
def check(s: State) -> Literal["generate",END]: return END if s["attempts"] >= 2 else "generate"
g=StateGraph(State); g.add_node("generate",generate); g.add_edge(START,"generate"); g.add_conditional_edges("generate",check)
if __name__ == "__main__": print(g.compile().invoke({"attempts":0,"draft":""}))
