"""Make the smallest useful HTTP GET request."""

import requests


def main() -> None:
    response = requests.get("https://example.com", timeout=10)
    response.raise_for_status()

    print("Status code:", response.status_code)
    print("First 200 characters of the response:")
    print(response.text[:200])


if __name__ == "__main__":
    main()
