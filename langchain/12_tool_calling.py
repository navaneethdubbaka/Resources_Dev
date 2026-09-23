from langchain_core.tools import tool
@tool
def multiply(first: int, second: int) -> int:
    """Multiply two integers."""
    return first * second
if __name__ == "__main__": print(multiply.invoke({"first": 6, "second": 7}))
