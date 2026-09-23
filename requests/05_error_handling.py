"""Handle network, timeout, and HTTP-status failures safely."""

import requests


def get_status(url: str) -> int | None:
    """Return a successful status code, or explain why the request failed."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return None

    print(f"Request succeeded with status {response.status_code}")
    return response.status_code


if __name__ == "__main__":
    # This endpoint intentionally returns 404 so the error path is visible.
    get_status("https://httpbin.org/status/404")
