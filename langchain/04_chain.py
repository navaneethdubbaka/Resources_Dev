from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
prompt = PromptTemplate.from_template("Explain {topic} in one sentence.")
local_model = RunnableLambda(lambda value: AIMessage(content=f"Offline model received: {value.text}"))
chain = prompt | local_model | StrOutputParser()
if __name__ == "__main__": print(chain.invoke({"topic": "FastAPI"}))
