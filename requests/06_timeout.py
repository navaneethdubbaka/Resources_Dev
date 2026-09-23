"""Set a time limit so a slow server cannot block the program forever."""

import requests


def get_with_short_timeout(url: str, timeout_seconds: float = 1.0) -> bool:
    try:
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.Timeout:
        print(f"Timed out after {timeout_seconds} second(s).")
        return False
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return False

    print("Request completed before the timeout.")
    return True


if __name__ == "__main__":
    # httpbin waits three seconds; the one-second timeout demonstrates the failure.
    get_with_short_timeout("https://httpbin.org/delay/3")
