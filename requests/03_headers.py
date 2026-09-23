"""Send descriptive metadata with request headers."""

import requests


def main() -> None:
    headers = {
        "Accept": "application/json",
        "User-Agent": "ai-engineering-day2/1.0",
    }
    response = requests.get("https://httpbin.org/headers", headers=headers, timeout=10)
    response.raise_for_status()

    print("Headers seen by the server:")
    print(response.json()["headers"])


if __name__ == "__main__":
    main()
