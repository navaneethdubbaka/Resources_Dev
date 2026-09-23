from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
class State(TypedDict): request: str; result: str
def classify(state: State): return {}
def route(state: State) -> Literal["answer","calculate"]: return "calculate" if state["request"].startswith("add ") else "answer"
def answer(state: State): return {"result":"This is a question."}
def calculate(state: State): return {"result":str(sum(map(int,state["request"].split()[1:])))}
graph=StateGraph(State); graph.add_node("classify",classify); graph.add_node("answer",answer); graph.add_node("calculate",calculate)
graph.add_edge(START,"classify"); graph.add_conditional_edges("classify",route); graph.add_edge("answer",END); graph.add_edge("calculate",END)
if __name__ == "__main__": print(graph.compile().invoke({"request":"add 2 3"}))
