from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
class State(TypedDict): count: int
def increment(s: State): return {"count":s["count"]+1}
g=StateGraph(State); g.add_node("increment",increment); g.add_edge(START,"increment"); g.add_edge("increment",END); app=g.compile(checkpointer=MemorySaver())
if __name__ == "__main__": print(app.invoke({"count":0},{"configurable":{"thread_id":"lesson-1"}}))
