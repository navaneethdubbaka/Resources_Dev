from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
class Lesson(BaseModel):
    topic: str
    summary: str
    difficulty: str = Field(pattern="^(beginner|intermediate)$")
if __name__ == "__main__":
    print(PydanticOutputParser(pydantic_object=Lesson).parse('{"topic":"JSON","summary":"Structured text data.","difficulty":"beginner"}'))
