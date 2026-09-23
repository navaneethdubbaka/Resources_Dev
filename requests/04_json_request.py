"""Read JSON returned by an API and access its fields."""

import requests


def main() -> None:
    response = requests.get("https://jsonplaceholder.typicode.com/todos/1", timeout=10)
    response.raise_for_status()

    data = response.json()
    print("Whole JSON object:", data)
    print("Title:", data["title"])
    print("Completed:", data["completed"])


if __name__ == "__main__":
    main()
