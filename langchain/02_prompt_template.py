from langchain_core.prompts import PromptTemplate
prompt = PromptTemplate.from_template("Explain {topic} to a {audience}.")
if __name__ == "__main__": print(prompt.format(topic="HTTP", audience="beginner"))
