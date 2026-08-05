"""Generic SportRadar API client."""

from __future__ import annotations

import random
import time
from typing import Any

import requests

from src.utils.config import (
    REQUEST_TIMEOUT_SECONDS,
    SPORTRADAR_API_KEY,
    SPORTRADAR_BASE_URL,
)


class SportRadarAPIError(RuntimeError):
    """Raised when a SportRadar request fails."""


def get_json(
    endpoint: str,
    max_retries: int = 5,
    backoff_seconds: float = 5.0,
) -> dict[str, Any]:
    """
    Request one SportRadar endpoint and return decoded JSON.

    Retries temporary rate-limit and server errors with exponential
    backoff. Permanent 4xx responses fail immediately.
    """

    if not SPORTRADAR_API_KEY:
        raise SportRadarAPIError(
            "SPORTRADAR_API_KEY is missing. Add it to your .env file."
        )

    endpoint = endpoint.lstrip("/")
    url = f"{SPORTRADAR_BASE_URL}/{endpoint}"

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url,
                headers={
                    "accept": "application/json",
                    "x-api-key": SPORTRADAR_API_KEY,
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            if response.status_code == 429 or response.status_code >= 500:
                if attempt >= max_retries:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    try:
                        wait_seconds = float(retry_after)
                    except ValueError:
                        wait_seconds = backoff_seconds * (2**attempt)
                else:
                    wait_seconds = backoff_seconds * (2**attempt)

                # Small jitter prevents repeated synchronized retries.
                wait_seconds += random.uniform(0.0, 1.0)
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            break

        except requests.RequestException as exc:
            status = getattr(exc.response, "status_code", None)
            body = getattr(exc.response, "text", "")

            raise SportRadarAPIError(
                "SportRadar request failed. "
                f"status={status}, endpoint={endpoint}, body={body[:500]}"
            ) from exc
    else:
        raise SportRadarAPIError(
            f"SportRadar request exhausted retries for {endpoint}."
        )

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
