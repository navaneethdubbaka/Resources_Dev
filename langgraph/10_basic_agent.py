from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): message: str; tool_result: str; answer: str
def agent(s: State): return {"answer":s["tool_result"] or "I can answer directly."}
def route(s: State) -> Literal["tool",END]: return "tool" if s["message"].startswith("add ") and not s["tool_result"] else END
def tool(s: State): return {"tool_result":str(sum(map(int,s["message"].split()[1:])))}
g=StateGraph(State); g.add_node("agent",agent); g.add_node("tool",tool); g.add_edge(START,"agent"); g.add_conditional_edges("agent",route); g.add_edge("tool","agent")
if __name__ == "__main__": print(g.compile().invoke({"message":"add 20 22","tool_result":"","answer":""}))
