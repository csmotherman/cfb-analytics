"""Minimal CFBD REST client for immutable raw acquisition."""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL = "https://api.collegefootballdata.com"
CLASSIFICATION = "fbs"


class CfbdError(RuntimeError):
    pass


@dataclass
class CfbdResponse:
    url: str
    status_code: int
    payload: Any
    raw_bytes: bytes
    headers: dict[str, str]


class CfbdClient:
    def __init__(self, api_key: str | None = None, timeout: float = 60.0) -> None:
        token = api_key or os.getenv("CFBD_API_KEY")
        if not token:
            raise CfbdError("CFBD_API_KEY is not set")
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CfbdClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get_json(self, path: str, params: dict[str, Any], retries: int = 4) -> CfbdResponse:
        clean_params = {k: v for k, v in params.items() if v is not None}
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                response = self._client.get(path, params=clean_params)
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < retries:
                        time.sleep((2**attempt) + random.random())
                        continue
                response.raise_for_status()
                raw = response.content
                payload = json.loads(raw)
                return CfbdResponse(
                    url=str(response.request.url),
                    status_code=response.status_code,
                    payload=payload,
                    raw_bytes=raw,
                    headers={k.lower(): v for k, v in response.headers.items()},
                )
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep((2**attempt) + random.random())
                    continue
                break
        raise CfbdError(f"CFBD request failed: {path} {clean_params}: {last_error}")

    def calendar(self, season: int) -> CfbdResponse:
        return self.get_json("/calendar", {"year": season})

    def games(self, season: int, week: int, season_type: str) -> CfbdResponse:
        return self.get_json(
            "/games",
            {"year": season, "week": week, "seasonType": season_type, "classification": CLASSIFICATION},
        )

    def drives(self, season: int, week: int, season_type: str) -> CfbdResponse:
        return self.get_json(
            "/drives",
            {"year": season, "week": week, "seasonType": season_type, "classification": CLASSIFICATION},
        )

    def plays(self, season: int, week: int, season_type: str) -> CfbdResponse:
        return self.get_json(
            "/plays",
            {"year": season, "week": week, "seasonType": season_type, "classification": CLASSIFICATION},
        )

    def lines(self, season: int, week: int, season_type: str = "regular") -> CfbdResponse:
        """Return the CFBD betting-line feed for one season/week partition.

        The v2 CFBD /lines endpoint does not expose the classification filter used
        by /games. Callers should join the returned game IDs back to the authoritative
        FBS-vs-FBS schedule before using market data in a product surface.
        """
        return self.get_json(
            "/lines",
            {"year": season, "week": week, "seasonType": season_type},
        )

    def teams(self) -> CfbdResponse:
        """Return CFBD team metadata, including logos and brand fields.

        The endpoint contains teams across classifications. Product callers are
        responsible for retaining only rows whose classification is ``fbs``.
        """
        return self.get_json("/teams", {})
