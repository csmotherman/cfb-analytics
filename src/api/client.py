"""
Generic SportRadar API client.
"""

import requests

from src.utils.config import BASE_URL, HEADERS


def get(endpoint: str) -> dict:
    """
    Send a GET request to the SportRadar API.

    Example:
        get("games/2025/REG/schedule.json")
    """

    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(url, headers=HEADERS)

    response.raise_for_status()

    return response.json()