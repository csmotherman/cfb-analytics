"""Generic CollegeFootballData API client."""

from __future__ import annotations

from typing import Any

import requests

from src.utils.config import (
    CFBD_API_KEY,
    CFBD_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
)


class CFBDApiError(RuntimeError):
    """Raised when a CollegeFootballData request fails."""


def get_json(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Request one CFBD endpoint and return decoded JSON."""

    if not CFBD_API_KEY:
        raise CFBDApiError(
            "CFBD_API_KEY is missing. Add it to your .env file."
        )

    endpoint = endpoint.lstrip("/")
    url = f"{CFBD_BASE_URL}/{endpoint}"

    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {CFBD_API_KEY}",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status = getattr(exc.response, "status_code", None)
        body = getattr(exc.response, "text", "")

        raise CFBDApiError(
            "CFBD request failed. "
            f"status={status}, endpoint={endpoint}, body={body[:500]}"
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise CFBDApiError(
            f"CFBD returned invalid JSON for {endpoint}."
        ) from exc
