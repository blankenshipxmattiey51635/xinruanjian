"""Normalized quote objects shared by real quote providers and the UI."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Quote:
    """A single real market quote normalized across providers."""

    symbol: str
    name: str
    market: str
    source: str
    price: float | None = None
    change_amount: float | None = None
    change_percent: float | None = None
    open_price: float | None = None
    previous_close: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    volume: float | None = None
    turnover: float | None = None
    bid1: float | None = None
    ask1: float | None = None
    turnover_rate: float | None = None
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    total_market_value: float | None = None
    float_market_value: float | None = None
    week52_high: float | None = None
    week52_low: float | None = None
    pre_market_price: float | None = None
    post_market_price: float | None = None
    fetched_at: str = ""
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
