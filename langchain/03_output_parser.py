from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
if __name__ == "__main__": print(StrOutputParser().invoke(AIMessage(content="Parsed model text.")))
