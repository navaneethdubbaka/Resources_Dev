"""Send a JSON request body with HTTP POST."""

import requests


def main() -> None:
    payload = {"name": "Ada", "topic": "HTTP POST"}
    response = requests.post("https://httpbin.org/post", json=payload, timeout=10)
    response.raise_for_status()

    data = response.json()
    print("Server received this JSON:", data["json"])


if __name__ == "__main__":
    main()
