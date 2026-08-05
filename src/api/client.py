"""Generic SportRadar API client."""

from __future__ import annotations

from typing import Any

import requests

from src.utils.config import (
    REQUEST_TIMEOUT_SECONDS,
    SPORTRADAR_API_KEY,
    SPORTRADAR_BASE_URL,
)


class SportRadarAPIError(RuntimeError):
    """Raised when a SportRadar request fails."""


def get_json(endpoint: str) -> dict[str, Any]:
    """
    Request one SportRadar endpoint and return decoded JSON.

    Example
    -------
    get_json("games/2025/REG/schedule.json")
    """

    if not SPORTRADAR_API_KEY:
        raise SportRadarAPIError(
            "SPORTRADAR_API_KEY is missing. Add it to your .env file."
        )

    endpoint = endpoint.lstrip("/")
    url = f"{SPORTRADAR_BASE_URL}/{endpoint}"

    try:
        response = requests.get(
            url,
            headers={
                "accept": "application/json",
                "x-api-key": SPORTRADAR_API_KEY,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status = getattr(exc.response, "status_code", None)
        body = getattr(exc.response, "text", "")

        raise SportRadarAPIError(
            f"SportRadar request failed. "
            f"status={status}, endpoint={endpoint}, body={body[:500]}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise SportRadarAPIError(
            f"SportRadar returned invalid JSON for {endpoint}."
        ) from exc

    if not isinstance(data, dict):
        raise SportRadarAPIError(
            f"Expected a JSON object from {endpoint}, "
            f"received {type(data).__name__}."
        )

    return data