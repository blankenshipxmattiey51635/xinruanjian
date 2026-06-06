"""Tiny standard-library HTTP client used by quote providers.

The project still lists requests for future modules, but phase-two providers use
urllib so tests and basic quote fetching work even before optional packages are
installed.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HttpClientError(RuntimeError):
    pass


class UrllibResponse:
    def __init__(self, body: bytes, status: int) -> None:
        self.body = body
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise HttpClientError(f"HTTP {self.status}")

    def json(self) -> dict[str, Any]:
        return json.loads(self.body.decode("utf-8"))


class UrllibSession:
    def get(self, url: str, **kwargs: Any) -> UrllibResponse:
        params = kwargs.get("params") or {}
        headers = kwargs.get("headers") or {}
        timeout = kwargs.get("timeout") or 4.0
        full_url = f"{url}?{urlencode(params)}" if params else url
        request = Request(full_url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                return UrllibResponse(response.read(), response.status)
        except (HTTPError, URLError, TimeoutError) as exc:
            raise HttpClientError(str(exc)) from exc
