"""Contracts for real market/news data sources.

Phase one intentionally does not fabricate quote data. Providers return a clear
unavailable result until a real source adapter is configured in later phases.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class DataResult:
    ok: bool
    source: str
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    message: str = ""


class QuoteProvider(Protocol):
    name: str

    def get_quote(self, symbol: str, market: str) -> DataResult:
        """Fetch one real quote or report why real data is unavailable."""


class NewsProvider(Protocol):
    name: str

    def search_news(self, keyword: str) -> DataResult:
        """Fetch real news or report why real data is unavailable."""
